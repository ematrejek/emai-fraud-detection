# Project Brief: Suspicious application classification algorithm \- EmAI Fraud Detection v1

## 11.06.2025

# 1\. Project overview

This project aims to develop a Python-based algorithm to automate the identification of **"suspicious" or "low-quality"** mobile applications. The **core problem** is the proliferation of applications that generate low-quality traffic, characterized by high Click-Through Rates (CTRs) and low or no conversions, which negatively impacts advertising campaign performance and the reputation among our clients. This initiative, stemming from the "Santa Clara" case analysis, focuses on creating a proactive mechanism to flag **potentially fraudulent** applications before they can cause significant issues. The final algorithm will serve as a first step in building a more robust fraud detection system by systematically labeling potentially problematic inventory.

# 2\. Goals and objectives

The primary goal is to **create an automated classification tool that assigns a "suspicious" label to applications based on a set of predefined rules and publicly available data**.

**Key Objectives:**

* **Determine a list of unwished keywords, threshold of an app’s age, threshold of number of downloads and unwished developer domains**  
* **Develop a keyword-based filter:** Implement a system to scan application IDs for a list of keywords associated with low-quality apps (e.g., "prank," "wallpaper," "fart").  
* **Integrate Google Play Scraper:** Utilize the google-play-scraper Python library to fetch key metadata for any given application.  
* **Define "red flag" metrics:** Establish rules based on scraped application characteristics, including:  
  * Low number of downloads.  
  * Recent release date (app age).  
  * Developer information (domain, etc.).  
* **Implement classification logic:** Build a scoring or rule-based engine that combines keyword analysis and metadata flags to produce a final classification.

# 3\. Scope

#### **In Scope**

* **Core functionality:** A Python algorithm that takes a mobile application ID (e.g., com.example.fartprank) as input and returns a classification (e.g., "Suspicious" / "Clear").  
* **Data sources:** The algorithm will exclusively use:  
  1. The application ID string itself.  
  2. Data retrieved via the google-play-scraper Python library (e.g., installs, release date, developer name).  
* **Methodology:** The project will involve creating and maintaining an internal list of suspicious keywords and establishing thresholds for the "red flag" metrics. More about the methodology is provided in the second section.

#### **Out of Scope**

* **Analysis of internal metrics:** The algorithm will not analyze internal or client-side data such as CTRs, conversion rates, or re-engagement metrics.  
* **External tool integration:** Integration with third-party verification services (e.g., DoubleVerify, MCP) is not part of this project.  
* **User Interface (UI):** This project is focused solely on the development of the back-end algorithm.

# 4\. General methodology & Technical specification

The algorithm will process a given application ID through the following steps:

1. **Keyword Analysis:** The input app ID will be checked against a curated list of keywords known to be associated with low-quality or suspicious apps.  
2. **Data scraping:** If the app ID passes the initial check or for further verification, the google-play-scraper library will be called to fetch its details from the Google Play Store.  
3. **Red flag identification:** The scraped data will be analyzed against predefined criteria:  
   * **Number of downloads:** Flagged if below a specified threshold.  
   * **Application age:** Flagged if the application is newly released.  
   * **Name similarity:** The app's name will be compared to a database of known fraudulent apps to flag close matches.  
4. **Classification:** A final score or label will be assigned based on the weighted combination of the flags triggered in the previous steps. An application with multiple red flags (e.g., contains a keyword *and* has very few downloads) will be classified as "Suspicious."  
* **Technology Stack:**  
  * **Language:** Python  
  * **Libraries:** google-play-scraper, pandas

### **5\. Success Metrics**

* The algorithm's ability to correctly identify applications that are later confirmed to be sources of invalid traffic.  
* The creation of a labeled dataset of applications that can be used for future, more advanced fraud detection models.  
* A measurable reduction in the manual effort required to identify and block low-quality application inventory (to be tested with the use of A/B tests on a sample advertiser)

