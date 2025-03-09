This project was undertaken to scrape Job Descriptions from Hiring Cafe website. 
This is an infinite scrolling website, that contains multiple boxes containing jobs for all the available companies.
The job boxes contain 'View All' button, when clicked, redirects you to all the jobs for that particular company.
On the redirected website, there are multiple boxes, when clicked, contains 'Full View' button, when clicked redirects to the full Job Description.

The logic used by me is:
a. Scroll till the end of the page (it is an infinite scrolling website)
b. Save the page source into a BeautifulSoup element
c. Extract the href link from the "View All' button and save all the href links into a pickle file.
d. Using playwright, click on each job box and extract href link from 'Full View' button and store it inside a pickle file.
e. Load those links using Requests library and save the html inside beautifulsoup element. 
f. Using etree from lxml library for xpath, extract all the job descriptions and save it into a csv file.

Note : 
a. After installing playwright in your environment, enter this line into your terminal - 
playwright install chromium

b. Install Chromedriver from its official website for selenium setup.
