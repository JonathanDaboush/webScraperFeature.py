#pls note that my focus in this project is too create optimal routes
#so for warehouse genheration I used chatgpt

# warehouse_structures.py
# Minimal, reusable warehouse grid generator.
# Produces: occupancy numpy arrays (0 free, 1 shelf, 2 drop, 3 pickup, 4 obstacle)
# Exposes: make_map(...), sample_tasks(...), save_map_csv/png(...)

import os, random, json
from typing import Tuple, List, Dict
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import pandas as pd

# -------------------------
# Utilities / palette
# -------------------------
PALETTE = {
    0: (250,250,250),   # free
    1: (30,30,30),      # shelf
    2: (0,200,0),       # drop
    3: (200,0,0),       # pickup
    4: (120,120,120),   # obstacle
}

# -------------------------
# Map generation primitives
# -------------------------
def generate_parallel_shelves(w:int, h:int, min_aisle:int, max_aisle:int, shelf_thickness:int=1) -> np.ndarray:
    occ = np.zeros((h,w), dtype=np.uint8)
    x = 0
    while x < w:
        aisle = random.randint(min_aisle, max_aisle)
        x += aisle
        if x >= w: break
        tw = shelf_thickness if random.random() < 0.9 else shelf_thickness+1
        for sx in range(x, min(w, x+tw)):
            occ[:, sx] = 1
        x += tw
    return occ

def generate_block_shelves(w:int, h:int, min_aisle:int, max_aisle:int, shelf_thickness:int=1) -> np.ndarray:
    occ = np.zeros((h,w), dtype=np.uint8)
    y = 0
    while y < h:
        aisle = random.randint(min_aisle, max_aisle)
        y += aisle
        if y >= h: break
        th = shelf_thickness if random.random() < 0.9 else shelf_thickness+1
        for sy in range(y, min(h, y+th)):
            occ[sy, :] = 1
        y += th
    # carve some holes so blocks are not too uniform
    holes = int(0.01*w*h)
    for _ in range(holes):
        ry = random.randint(0,h-1); rx = random.randint(0,w-1)
        occ[ry, rx] = 0
    return occ

def add_random_obstacles(occ:np.ndarray, prob:float) -> np.ndarray:
    h,w = occ.shape
    mask = (np.random.rand(h,w) < prob) & (occ==0)
    occ[mask] = 4
    return occ

def place_zones(occ:np.ndarray, multi_drop:bool=False, pick_count_range:Tuple[int,int]=(1,3)) -> Tuple[np.ndarray, Dict]:
    h,w = occ.shape
    zones = {'drop':[], 'pick':[]}
    # drop zones: prefer right/bottom edges
    drop_targets = []
    if multi_drop:
        count = 1 + int(random.random() < 0.6)
    else:
        count = 1
    for _ in range(count):
        tries = 0
        while tries < 500:
            tries += 1
            side = random.choice(['right','bottom','corner'])
            if side == 'right':
                x = w - 1
                y = random.randint(0, h-1)
            elif side == 'bottom':
                y = h - 1
                x = random.randint(0, w-1)
            else:
                x = random.randint(max(0,w-3), w-1)
                y = random.randint(max(0,h-3), h-1)
            if occ[y,x] == 0:
                occ[y,x] = 2
                zones['drop'].append((x,y))
                drop_targets.append((x,y))
                break
    # pick zones: prefer left/top edges or cells adjacent to shelves
    pick_count = random.randint(pick_count_range[0], pick_count_range[1])
    attempts = 0
    while len(zones['pick']) < pick_count and attempts < 2000:
        attempts += 1
        mode = random.choice(['left','top','adj_shelf','random'])
        if mode == 'left':
            x = 0; y = random.randint(0,h-1)
        elif mode == 'top':
            y = 0; x = random.randint(0,w-1)
        elif mode == 'adj_shelf':
            shelf_cells = list(zip(*np.where(occ==1)))
            if not shelf_cells:
                x = random.randint(0,w-1); y = random.randint(0,h-1)
            else:
                sy,sx = random.choice(shelf_cells)
                nx,ny = random.choice([(sx+1,sy),(sx-1,sy),(sx,sy+1),(sx,sy-1)])
                x,y = nx,ny
        else:
            x = random.randint(0,w-1); y = random.randint(0,h-1)
        if 0 <= x < w and 0 <= y < h and occ[y,x] == 0:
            occ[y,x] = 3
            zones['pick'].append((x,y))
    return occ, zones

# -------------------------
# High-level map factory
# -------------------------
def make_map(w:int=24, h:int=16,
             style:str='parallel', min_aisle:int=1, max_aisle:int=4,
             shelf_thickness:int=1, obstacle_prob:float=0.02, multi_drop_prob:float=0.35,
             pick_count_range:Tuple[int,int]=(1,3),
             morphology_clean:bool=True) -> Tuple[np.ndarray, Dict]:
    """
    Create a single warehouse occupancy grid.
    style: 'parallel' or 'block' (others can be added)
    Returns occupancy array and metadata dict
    """
    if style not in ('parallel','block'):
        style = 'parallel'
    if style == 'parallel':
        occ = generate_parallel_shelves(w,h,min_aisle,max_aisle,shelf_thickness)
    else:
        occ = generate_block_shelves(w,h,min_aisle,max_aisle,shelf_thickness)

    occ = add_random_obstacles(occ, obstacle_prob)
    multi_drop = random.random() < multi_drop_prob
    occ, zones = place_zones(occ, multi_drop=multi_drop, pick_count_range=pick_count_range)

    if morphology_clean:
        # remove tiny islands, fill small holes in shelves
        shelf_mask = (occ==1).astype(np.uint8)
        shelf_mask = ndimage.binary_closing(shelf_mask, structure=np.ones((2,2))).astype(np.uint8)
        occ[shelf_mask==1] = 1

    meta = {
        'w': w, 'h': h, 'style': style, 'min_aisle': min_aisle, 'max_aisle': max_aisle,
        'shelf_thickness': shelf_thickness, 'obstacle_prob': obstacle_prob,
        'multi_drop': multi_drop, 'num_shelves': int((occ==1).sum()), 'num_obstacles': int((occ==4).sum())
    }
    meta.update(zones)
    return occ, meta

# -------------------------
# Task sampling
# -------------------------
def sample_tasks(occ:np.ndarray, num_tasks:int=10, prefer_adjacent:bool=True) -> List[Dict]:
    h,w = occ.shape
    candidates = []
    # pickups: cells adjacent to shelf or marked pick zones
    for y in range(h):
        for x in range(w):
            if occ[y,x] == 3:
                candidates.append((x,y))
            elif occ[y,x] == 0 and prefer_adjacent:
                # check 4-neighborhood for shelf
                for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                    nx,ny = x+dx, y+dy
                    if 0<=nx<w and 0<=ny<h and occ[ny,nx] == 1:
                        candidates.append((x,y)); break
            elif occ[y,x] == 0 and not prefer_adjacent:
                candidates.append((x,y))
    candidates = list(dict.fromkeys(candidates))  # unique, keep order
    if not candidates:
        # fallback: any free cell
        candidates = list(zip(*np.where(occ==0)))
    drop_cells = list(zip(*np.where(occ==2)))
    if not drop_cells:
        drop_cells = [(w-1,h-1)]
    tasks = []
    for i in range(min(num_tasks, len(candidates))):
        px,py = random.choice(candidates)
        dx,dy = random.choice(drop_cells)
        tasks.append({'task_id': i, 'pickup_x': int(px), 'pickup_y': int(py), 'drop_x': int(dx), 'drop_y': int(dy), 'priority': random.choice([1,1,2,3])})
    return tasks

# -------------------------
# Save / visualization
# -------------------------
def save_map_csv(occ:np.ndarray, path:str):
    np.savetxt(path, occ, fmt='%d', delimiter=',')

def visualize_map(occ:np.ndarray, cell_px:int=24, show_grid:bool=True) -> Image.Image:
    h,w = occ.shape
    img = Image.new('RGB', (w*cell_px, h*cell_px), (240,240,240))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        for x in range(w):
            c = PALETTE.get(int(occ[y,x]), (255,0,255))
            draw.rectangle([x*cell_px, y*cell_px, (x+1)*cell_px-1, (y+1)*cell_px-1], fill=c)
    if show_grid:
        for i in range(w+1):
            draw.line([(i*cell_px,0),(i*cell_px,h*cell_px)], fill=(200,200,200))
        for j in range(h+1):
            draw.line([(0,j*cell_px),(w*cell_px,j*cell_px)], fill=(200,200,200))
    return img

def save_visual(occ:np.ndarray, path:str, cell_px:int=24):
    img = visualize_map(occ, cell_px=cell_px)
    img.save(path)

def show_warehouse(w:int=24, h:int=16, style:str='parallel', **kwargs) -> Tuple[Image.Image, np.ndarray]:
    """
    Generate and display a warehouse map with visualization.
    Returns both the visual image and the grid structure.
    """
    occ, meta = make_map(w=w, h=h, style=style, **kwargs)
    img = visualize_map(occ)
    
    # Display the image (will show in notebook/IDE or save temporarily)
    try:
        img.show()  # This will open the image in default viewer
    except:
        print("Could not display image directly. Image object returned for manual display.")
    
    print(f"Generated {style} warehouse ({w}x{h})")
    print(f"Shelves: {meta['num_shelves']}, Obstacles: {meta['num_obstacles']}")
    print(f"Drop zones: {len(meta['drop'])}, Pick zones: {len(meta['pick'])}")
    
    return img, occ

def load_saved_visual(path:str) -> Image.Image:
    """
    Load and display a previously saved warehouse visualization.
    Returns the loaded image.
    """
    try:
        img = Image.open(path)
        img.show()  # Display the loaded image
        print(f"Loaded visualization from: {path}")
        return img
    except FileNotFoundError:
        print(f"Error: File not found at {path}")
        return None
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

# -------------------------
# Batch generator
# -------------------------
def generate_dataset(out_dir:str='synthetic_dataset', num_maps:int=200, map_kwargs:Dict=None, tasks_per_map:int=12):
    os.makedirs(out_dir, exist_ok=True)
    img_dir = os.path.join(out_dir,'images'); grid_dir = os.path.join(out_dir,'grids')
    os.makedirs(img_dir, exist_ok=True); os.makedirs(grid_dir, exist_ok=True)
    all_tasks = []
    metas = []
    map_kwargs = map_kwargs or {}
    for i in range(num_maps):
        # vary params lightly per map for diversity
        kwargs = dict(map_kwargs)
        if 'style' not in kwargs:
            kwargs['style'] = random.choice(['parallel','block'])
        if 'min_aisle' not in kwargs:
            kwargs['min_aisle'] = random.randint(1,2)
        if 'max_aisle' not in kwargs:
            kwargs['max_aisle'] = random.randint(2,4)
        occ, meta = make_map(**kwargs)
        grid_name = f"map_{i:04d}.csv"
        img_name = f"map_{i:04d}.png"
        save_map_csv(occ, os.path.join(grid_dir, grid_name))
        save_visual(occ, os.path.join(img_dir, img_name))
        tasks = sample_tasks(occ, num_tasks=tasks_per_map)
        for t in tasks:
            t['map_id'] = i
            all_tasks.append(t)
        meta['map_id'] = i
        metas.append(meta)

    pd.DataFrame(all_tasks).to_csv(os.path.join(out_dir,'tasks.csv'), index=False)
    with open(os.path.join(out_dir,'meta.json'),'w') as f:
        json.dump({'num_maps':num_maps, 'map_params':map_kwargs, 'maps':metas}, f, indent=2)
    print(f"Generated {num_maps} maps in {out_dir}. tasks.csv and images/grids saved.")
