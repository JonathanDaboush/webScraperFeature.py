from mrjob.job import MRJob
from mrjob.step import MRStep
import kagglehub
import os

# Download latest version
path = kagglehub.dataset_download("matiflatif/netflix-complete-stock-dataweekly-updated")

class netflixStock(MRJob):
    def steps(self):
        return [
            MRStep(mapper=self.mapper_get_ratings,
                   reducer=self.reducer_count_ratings)
        ]

    def mapper_get_ratings(self, _, line):
        # Split the line into fields
        fields = line.split(',')
        # Extract the date and closing price
        date = fields[0]
        closing_price = float(fields[4])
        # Yield the date and closing price
        yield date, closing_price

    def reducer_count_ratings(self, date, closing_prices):
        # Calculate the average closing price for the date
        total = sum(closing_prices)
        count = len(closing_prices)
        average = total / count
        # Yield the date and average closing price
        yield date, average

if __name__ == '__main__':
    # Ensure the dataset is in the correct format and accessible
    input_path = os.path.join(path, 'netflix_stock_data.csv')
    netflixStock.run(input_path)