
# Module 1 Final Project 



**Description: Our client has created a new movie studio, but need's consultation to help them better understand this new market they are entering. In this project, we explore and analyze movie-related data to provide insights on ideal movie characteristics that contribute to success.**

### Datasets
For this project, we use the provided datasets in .csv and .tsv format from IMDB, TMDB, and TN databases. We store all these datasets in a SQLITE databases for ease of access and querying

### Modules

I've created a few modules that I use to complete my analysis, found in the "module1_util_scripts" folder:

- loader.py - contains methods for reading the raw datasets in .csv and .tsv formats as pandas dataframes, and uploading dataframes onto SQLITE3 databases
- sqlreader.py - contains methods for reading SQL queries and returning query results as pandas dataframes
- cleaner.py - contains methods for initial cleaning of raw datasets
- grapher.py - contains methods for plotting various types of graphs with some standard attributes

### Configs
- thresholds.json - configuration file used in the cleaner.py module to set specifications/parameters for cleaning

### Notebooks/Questions

1. question_1.ipynb - What were the top 3 highest rated movie genres in the last decade? 
2. question_2.ipynb - Which actors and directors contributed to more successful movies in the top 3 genres?
3. question_3.ipynb - For the top 3 genres, what is the average domestic and foreign YoY gross revenue? What is the relationship between production budget and gross spread?
4. question_4.ipynb - What is the relationship between movie runtime and ratings?

### Presentations

1. presentation.pdf

### Conclusion

The top rated movie genre in the dataset is "Biography". Director Ezra Edelman has a portfolio of the highest rated movies directed on average, and actor Aamir Khan has a portfolio of the highest rated movies acted in on average (Disclaimer* This is not to say they will be successful in all future Biography productions, other considerations such as subject, market, country etc. have to be taken into account as well). Biographies have a weak positive correlation between production budgets and gross spreads, and separately virtually no correlation between runtime and ratings, indicating that the studio doesn't have to be preoccupied with thinking it needs a high budget to product a successful project. 

### Recommendation

The studio can try to start off with producing Biographies. There have been numerous highly successful Biographies with relatively low production budgets, so financially it is a relatively lower risk. Of course, all the other factors not discussed in this project should be naturally taken into account, such as quality of screenplay, character, subject, picture quality etc.
