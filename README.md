# Synengco Recruitment Challenge

Recruitment challenge based on AEMO electricity demand 

## Accompanying Notes

### Overall approach

The desired function of the end product drives the creative design of its structure, and the structure drives the decisions about the process for building it and the resources consumed along the way. So first I have to identify what this product has to do - the behaviour when it is in the hands of the operator.

On first reading of the challenge spec, there is actually no functionality explicitly requested! The end product must contain data and a visualisation and the method of visualisation is left open. The only hint of behaviour performed for the operator is in the "bonus points" list which includes allowing the user to select which day to visualise.
 All information that was requested in the spec could be delivered as precomputed static data files and image files in the project repository. However, given the circumstances of the challenge, I infer that it is better to show how this data is generated, and it is best if the derivation method is demonstrated by having the reviewers execute the program that generates the data and the visualisations. This is not explicitly requested but is now a design decision and a fair one given the circumstances.

Another stated purpose of the project is assessing the "ability to interact effectively with colleagues and mentor", which implies I should do that even if on first glance the specification seems complete and no further interaction should be necessary to do the data analysis. A more iterative approach with phased delivery would also be a close match for the company's project methodology. So confirming the requirements of the product and the feature delivery schedule seem like two good reasons for doing this "colleague interaction".

Perhaps the entire spec will change in the first phone call? So following the agile methodology, the first thing to deliver is an initial refined system requirements specification and to get validation of these requirements. The decision about incremental delivery can then also be made.

The steps in this approach will be:

1. Treat the Challenge Instructions as a customer's Stakeholder's Needs and Requirements, and use that to write a first version of System Requirements Specification containing the developer's understanding of the requirements.

2. Draw a behaviour diagram showing the interaction of the product with the user(s).

3. Make initial system architecture diagram showing only the inputs and outputs. Use this to think of more questions for the first discussion, as the customer's time is valuable and so meetings should be very productive.

4. Contact customer (colleagues) to validate the developer's understanding of the high level requirements.

5. Confirm the system architecture diagrams with the customer. Also check for system constraints such as:
	* whether downloading various Python packages from the Internet is permitted, or does the solution need to work within a predefined limited set of packages?
	* does the solution have to execute within a time limit?
	* Do they need training material provided and a training session conducted about using the solution?  
	 (Probably not needed, but this is offered in the spirit of simulating a real project.)

6. Decompose the system architecture to the next level to show how data products will be computed and how the first simple visualisation will be done.

7. Implement the data wrangling of the April 2020 data. Implement the computing of the historic baseline data. Deliver these to the customer (via public repository push) if that has been agreed in the first discussion.

8. Implement the comparison and the initial visualisation output of the April 2020 comparison. Deliver this (if that was agreed).  At this point all of the deliverables should have technically been complete and delivered. Ask if a time needs to be arranged to conduct "training" on the solution. 

9. Pitch ideas for a more complex interactive visualisation and get user feedback about them. Make a more complex interactive visualisation of some sort. Deliver that. Get feedback on it.


## System Requirements Specification

As this may involve mathematical formulas it is in separate documents, as an OpenOffice writer (source) file and the authoritative version is the PDF export of it.
[SysRS.pdf](SysRS.pdf)

## System Behaviour and Architecture

![System behaviour and architecture.png](System%20behaviour%20and%20architecture.png)

## Installation and setup

```
$ git clone https://github.com/amcrae/recruitment-challenge-2020  
$ pip3 install -r requirements.txt 
```


## System Operation & User's Guide

Just run the main script on a console which has a graphical desktop environment.

```
$ python3 compute.py
```

