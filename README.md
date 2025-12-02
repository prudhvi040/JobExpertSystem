# Job Advisor Expert System (Python + Experta)

A rule-based expert system built using **Experta (PyKnow)** to recommend suitable job roles based on a user's profile.  
The system uses a classic expert system design: facts, rules, forward chaining, and explainability via rule traces.


## 🎯 Overview

This expert system evaluates a user's job-related characteristics such as:

- work environment preference (indoor / hybrid / outdoor)  
- experience and education  
- skill match percentage  
- physical capability  
- driving license and shift willingness  
- remote-working compatibility  
- salary expectation  

Based on these inputs, the rule engine recommends one of:

- **ADMIN**  
- **IT**  
- **DELIVERY**  
- **SALES**  
- **REMOTE / FREELANCE**

A trace of fired rules is also returned for full transparency.


## 🧠 Tech Stack

- **Python 3.8+**
- **Experta (PyKnow)** – rule engine framework
- **Dataclasses** – for clean profile representation
  

## 🧩 How the Expert System Works

### 1. **Facts**

- Profile — user information  
- Recommendation — final output  


### 2. **Inference Engine**

The engine:

1. Selects a branch (indoor / hybrid / outdoor)  
2. Applies rules specific to that branch  
3. Adjusts the recommendation using salary and skill thresholds  
4. Outputs the most specific recommendation  
5. Returns an explanation trace  


### 3. **Rule Categories**

- **Branch Rules**  
- **Indoor Rules**  
- **Hybrid Rules**  
- **Outdoor Rules**  
- **Adjustment Rules**  
- **Fallback Rules**


### 4. **Flowchart**

A visual version of this logic is included.  
It shows the decision path from inputs → branch → rules → final recommendation.


## 📝 Key Features

- Clean rule-based architecture  
- Human-understandable logic  
- Explainability: each rule logs why it fired  
- Small, readable codebase  
- Runs without external services or ML models  
- Adjustable thresholds (salary_med, skill limits)  
