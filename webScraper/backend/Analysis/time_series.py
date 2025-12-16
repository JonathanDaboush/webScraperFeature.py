from typing import List, Dict
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from Persistance.repository import Repository
from Persistance.crawler import Page, CrawlJob, Request


class TimeSeriesAnalysis:
    """Time-based analysis of crawling activity and content."""
    
    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()
    
    def get_pages_by_date(self, start_date: datetime = None, end_date: datetime = None) -> List[Page]:
        """Get pages found within a date range."""
        query = self.repo.session.query(Page)
        
        if start_date:
            query = query.filter(Page.date_found >= start_date)
        if end_date:
            query = query.filter(Page.date_found <= end_date)
        
        return query.order_by(Page.date_found).all()
    
    def pages_per_day(self, days: int = 30) -> Dict[str, int]:
        """Count pages found per day for the last N days."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        pages = self.get_pages_by_date(start_date, end_date)
        
        # Group by date
        pages_by_day = defaultdict(int)
        for page in pages:
            date_key = page.date_found.strftime('%Y-%m-%d')
            pages_by_day[date_key] += 1
        
        return dict(sorted(pages_by_day.items()))
    
    def pages_per_hour(self, hours: int = 24) -> Dict[int, int]:
        """Count pages found per hour for the last N hours."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=hours)
        
        pages = self.get_pages_by_date(start_date, end_date)
        
        # Group by hour
        pages_by_hour = defaultdict(int)
        for page in pages:
            hour = page.date_found.hour
            pages_by_hour[hour] += 1
        
        return dict(sorted(pages_by_hour.items()))
    
    def crawl_job_timeline(self) -> List[Dict]:
        """Get timeline of all crawl jobs."""
        jobs = self.repo.get_all_crawl_jobs()
        
        timeline = []
        for job in jobs:
            requests = self.repo.get_requests_by_job(job.id)
            pages = [r.page for r in requests if r.page]
            
            timeline.append({
                "job_id": job.id,
                "search_query": job.search_query,
                "started": job.started,
                "total_requests": len(requests),
                "total_pages": len(pages),
                "crawled_pages": sum(1 for p in pages if p.crawled)
            })
        
        return sorted(timeline, key=lambda x: x["started"], reverse=True)
    
    def activity_by_domain_over_time(self, days: int = 30) -> Dict[str, Dict[str, int]]:
        """Track crawling activity per domain over time."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        pages = self.get_pages_by_date(start_date, end_date)
        
        # Group by domain and date
        activity = defaultdict(lambda: defaultdict(int))
        for page in pages:
            if page.domain:
                date_key = page.date_found.strftime('%Y-%m-%d')
                activity[page.domain.domain][date_key] += 1
        
        return {domain: dict(sorted(dates.items())) 
                for domain, dates in activity.items()}
    
    def peak_hours(self) -> Dict[str, int]:
        """Find peak crawling hours."""
        pages = self.repo.session.query(Page).all()
        
        hours = [page.date_found.hour for page in pages if page.date_found]
        hour_counts = Counter(hours)
        
        return dict(sorted(hour_counts.items(), key=lambda x: x[1], reverse=True))
    
    def growth_rate(self, days: int = 30) -> Dict:
        """Calculate growth rate of pages over time."""
        pages_by_day = self.pages_per_day(days)
        
        if not pages_by_day:
            return {"growth_rate": 0, "total_pages": 0, "average_per_day": 0}
        
        dates = sorted(pages_by_day.keys())
        total_pages = sum(pages_by_day.values())
        avg_per_day = total_pages / len(dates) if dates else 0
        
        # Calculate growth rate (simple linear)
        if len(dates) > 1:
            first_week = sum(pages_by_day.get(d, 0) for d in dates[:7])
            last_week = sum(pages_by_day.get(d, 0) for d in dates[-7:])
            growth_rate = ((last_week - first_week) / first_week * 100) if first_week > 0 else 0
        else:
            growth_rate = 0
        
        return {
            "growth_rate": round(growth_rate, 2),
            "total_pages": total_pages,
            "average_per_day": round(avg_per_day, 2),
            "days_analyzed": len(dates)
        }
    
    def request_success_rate_over_time(self, days: int = 30) -> Dict[str, Dict]:
        """Track request success rates over time."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        requests = self.repo.session.query(Request).filter(
            Request.date_requested >= start_date,
            Request.date_requested <= end_date
        ).all()
        
        # Group by date
        by_date = defaultdict(lambda: {"total": 0, "success": 0, "failed": 0})
        
        for req in requests:
            date_key = req.date_requested.strftime('%Y-%m-%d')
            by_date[date_key]["total"] += 1
            
            if req.status_code and 200 <= req.status_code < 300:
                by_date[date_key]["success"] += 1
            elif req.status_code:
                by_date[date_key]["failed"] += 1
        
        # Calculate success rates
        for date_key in by_date:
            total = by_date[date_key]["total"]
            success = by_date[date_key]["success"]
            by_date[date_key]["success_rate"] = round(success / total * 100, 2) if total > 0 else 0
        
        return dict(sorted(by_date.items()))
    
    def get_time_series_summary(self, days: int = 30) -> Dict:
        """Get comprehensive time series summary."""
        pages_daily = self.pages_per_day(days)
        growth = self.growth_rate(days)
        success_rate = self.request_success_rate_over_time(days)
        
        return {
            "period_days": days,
            "pages_per_day": pages_daily,
            "growth_metrics": growth,
            "success_rates": success_rate,
            "peak_hours": dict(list(self.peak_hours().items())[:5])
        }


# Example usage
if __name__ == "__main__":
    from Persistance.repository import Repository
    
    repo = Repository()
    time_analysis = TimeSeriesAnalysis(repo)
    
    print("Time Series Analysis:")
    print("=" * 60)
    
    # Pages per day
    print("\nPages Found Per Day (Last 7 days):")
    pages_daily = time_analysis.pages_per_day(days=7)
    for date, count in pages_daily.items():
        print(f"  {date}: {count} pages")
    
    # Growth rate
    print("\nGrowth Metrics:")
    growth = time_analysis.growth_rate(days=30)
    print(f"  Growth Rate: {growth['growth_rate']}%")
    print(f"  Total Pages: {growth['total_pages']}")
    print(f"  Average Per Day: {growth['average_per_day']}")
    
    # Peak hours
    print("\nPeak Crawling Hours:")
    peak = time_analysis.peak_hours()
    for hour, count in list(peak.items())[:5]:
        print(f"  Hour {hour}:00 - {count} pages")
    
    # Crawl job timeline
    print("\nCrawl Job Timeline:")
    timeline = time_analysis.crawl_job_timeline()
    for job in timeline[:5]:
        print(f"  Job {job['job_id']}: {job['search_query']} ({job['total_pages']} pages)")
    
    repo.close()
