// Each entry declares a title, a URL-safe slug, and a loader that dynamically imports the component.
export const pagesML = [
  { title: "Text Classifier", slug: "text-classifier", load: () => import("./TextClassifier") },
  { title: "Image Search",   slug: "image-search",   load: () => import("./ImageSearch") },
  { title: "Chatbot",        slug: "chatbot",        load: () => import("./Chatbot") },
];

export const pagesAnalysis = [
  { title: "Text Classifier", slug: "text-classifier", load: () => import("./TextClassifier") },
  { title: "Image Search",   slug: "image-search",   load: () => import("./ImageSearch") },
  { title: "Chatbot",        slug: "chatbot",        load: () => import("./Chatbot") },
];
// Optional: helper to find a page by slug
export const getPageBySlugML = (slug) => pagesML.find(p => p.slug === slug) || null;
export const getPageBySlugAnalysis = (slug) => pagesAnalysis.find(p => p.slug === slug) || null;