## Q1. What are the first 3–5 things EE-Eval must do in v1?
Answer:
- Maintain a profile for each individual employee.
- Provide secure access to the employee profile by the employee's manager, perhaps using groups. Managers should be specifically identified, and their groups should be private to them and their management chain. There should be some concept of hierarchy.
- The employee profile should track the employee's overall performance score for the last 3 years, and have a way to capture current input. The managers should be able to update the current year in real-time, documenting important points throughout the year, as a way to keep track of performance.
- There should be a way to manually enter the past years performance data, which is a single number between 0.00 and 5.00 for each year.
- There should be a workflow form that the manager would complete, which should derive a "Potential" score on a scale of 1 to 3. This workflow should ask the necessary questions as clearly and simply as possible to determine the employee's "potential" rating.
- There will be a "9-box_guidance.md" file that describes the whole 9-box concept (Sustained performance vs potential), with the intention that this information be presented to the managers intuitively in the frontend. This doc will contain guidance for how to rate employees, the language and messaging, the point and purpose for the 9-box, and how to interpret the employee's rating.
- A history of 9-box ratings should be maintained indefinitely for every employee.
- A history of performance ratings should be maintained indefinitely.
1.i. There should be a way to manipulate the 9-box performance criteria. This should be a global change, but it should only impact current and future 9-box ratings to preserve historical ratings. This criteria would be defined by HR or application global admin. The purpose is to take the numeric performance rating of 0.00-5.00 and map specific values to the Low, Medium, and High performance tiers.
- There should be a concept of multiple views of the application. First the "employee" view, which allows them to see limited data, such as comments that the manager may want to share with the employee throughout the year such as during 1:1 meetings which may occur weekly. Next, the "manager" view, which allows them to manage their team, by entering performance data, viewing the 9-box, leaving employee visible comments, manager private comments, etc. Additionally, there should be an "HR" view, which has permissions to review all employees, change hierarchy, update employee details, such as job titles, etc. as well as create new employees upon hire, and archive (but not delete) employees upon termination. Finally, there needs to be an "administrator" that can manipulate the deployment of the tool, such as tool access, permissions, groups, directory/SSO details, etc. Some of these details will come later in the roadmap.
- The 9-box presentation should have different views such as, The most recent "published" 9-box rating and comments (which would have been entered as part of the last annual performance review.), The current 9-box rating, based on the most up to date data gathered since the last published review. and a 9-box heatmap, that shows the employee's 9-box rating over time, potentially highlighting the employee's movement.
- there should be some feedback to the manager along the way if there is a material change in the employee's ratings based on historical patterns.
- there needs to be some trend tracking for ratings that may indicate upward, stable, or downward trends in an intuitive way to the manager so they can identify opportunities.
- as part of the performance review process, there needs to be a way to publish, or capture the review at the end of the year. This should include the manager entering a 0.00-5.00 score for performance, and filling out a questionnaire (or workflow as I mentioned it earlier) to determine potential. 

## Q2. Is the 9-box the center of the app, or just one output of a broader evaluation process?
Answer:
- There are 2 main goals of this app, 1. Provide a way to continuously capture performance data throughout the year, such as a part of 1:1 meetings with employees. This should help the manager complete the annual merit review by capturing things that may otherwise be forgotten, or prevent the manager from reviewing based solely on recent memory.  2. the 9-box is derived from the historical performance rating, and the workflow the manager completes throughout the year, capturing changes throughout the year. I envision the manager having a panel that has a number of statements and a slider for each on a scale of 1-3 that they can update at any time. each update is recorded, and previous versions can be reviewed. The 9-box is more of an output, but it should be the tool that helps the manager stay calibrated with other managers, and it should provide guidance on how to manage each employee, such as intervention, promotion, etc. based on the employee's 9-box position.

## Q3. Should managers enter scores directly, or answer structured questions that produce a suggested placement?
Answer:
- There are 2 axis of the 9-box: sustained performance, and potential. Sustained Performance should be a rolling 3-year average of the overall performance rating of the employee. potential should be a result of structured questions. as previously mentioned, the manager should be able to answer these questions at any time, keeping a real-time record and history. These realtime updates can be published as a permanent record at year-end review time, but throught the year, the manager should be able to update answers to the structured questions, and even provide an updated overall rating for performance. The overall rating for performance will be "trued up" with the official merit review score prior to publishing the 9-box rating for the year.

## Q4. Should the tool support only annual reviews at first, or also quarterly / ad hoc reviews?
Answer:
- Annual and ad-hoc reviews.

## Q5. Should employees ever log in, or is this strictly for HR and management?
Answer:
- Employees should be able to log in, and bea ble to see limited data, such as manager comments that the manager shares with them, and provide reply to comments. As a roadmap item, this may evolve into OKR tracking and milestones.


---

# 4B. Roles and permissions

## Q6. What user roles do you want initially?

Answer:
- HR admin
- Direct Manager
- Manager's Manager
- Employee, IT admin
- executive (which may be a group, for top level review and calibration purposes.) 
- Most of these roles I've already made mention of, except the executive, which should have a way to review a rating, and provide feedback (visible to the manager's manager), which would be an opportunity to adjust the rating before finally publishing it.

## Q7. Should managers only see their direct reports?
Answer:
- Managers should see only their direct reports, and subsequent levels below them.

## Q8. Should upper management see everyone below them?
Answer:
- Yes.

## Q9. Should HR be able to see everything?
Answer:
- yes.

## Q10. Should there be a distinction between viewing and editing sensitive records?
Answer:
- yes. There needs to be auditability. recording dates and times. 

---

# 4C. Evaluation model

## Q11. What are the two axes of your 9-box?
Commonly these are performance and potential, but define them as you want them used here.

Answer:
- When a 9-box is published, it will capture the current performance rating which is manually sourced from the employee's merit review (completed outside EE-Eval for now), and averaged with the previous two year's overall merit review scores. It will also capture the most current answer set of the structured questions for the potential. Once the 9-box is published a new term is started, where the manager can begin entering data throughout the year until next review cycle

## Q12. Do you want fixed rating scales, customizable scales, or both later?
Answer:
- The performance scale needs to be customizable. for example 0.00-2.99=low, 3.00-3.50=med, 3.51-5.0=hi. The potential should be an average (rounded to the nearest integer) of the structured question's answers, which would be 1-3. 

## Q13. Should evaluations support free-text evidence and attachments?
Answer:
- Yes.

## Q14. Should prior review periods be visible while writing a new review?
Answer:
- yes.

## Q15. Should the system store calibration history and changes to box placement over time?
Answer:
- yes.

---

# 4D. Sensitive HR workflows

## Q16. Do you want to track PIPs directly in v1, or only attach references/notes?
Answer:
- v1 can track PIP via attachments. Future versions can have a more structured approach.

## Q17. Should promotion recommendations be structured fields, narrative text, or both?
Answer:
- both

## Q18. Should there be a special confidentiality flag for especially sensitive cases?
Answer:
- Yes. There may be HR-only comments between the employee and HR. There may be comments that exclude upper levels of management between the employee and their manager and/or HR. There may be discssuion between a manager, and employee. Anything that is visible to the employee needs to be extremely clear to anyone entering anything. 

## Q19. Do you need an approval workflow for certain actions?
Answer:
- Approvals would be good for publishing the review. First step is to freeze the current year's data, capturing the most up to date data. This would put the review into something like release candidate mode, things can still be changed, but the changes should be captured differently as part of the final review, and not as part of the ad-hoc updates throughout the year, avoiding polluting the pregression trends throughout the year. This would also be the time where the manager would use this tool to write the merit review (which is done outside this tool) and gather the final overall performance score, which would then be entered into the 9-box as the final number for the year. This would allow the manager to then send this review to their manager, starting a feedback cycle, allowing things to be adjusted and accepted or declined. Once both parties have accepted, it would go on to calibration at the executive level, launching another feedback cycle. Once this cycle is completed, and all adjustments signed off by the executive(s) then it would become the final imutable version.

## Q20. Do you need full audit logs showing who viewed or changed records?
Answer:
- yes.

---

# 4E. Authentication and identity

## Q21. For local accounts, should HR create users manually?
Answer:
- yes, IT admins should be able to do this too.

## Q22. For LDAP later, do you expect role mapping from directory groups?
Answer:
- yes

## Q23. Do you want MFA eventually?
Answer:
- Yes

## Q24. Should password policy and lockout rules be configurable?
Answer:
- yes.

---

# 4F. Reporting and UX

## Q25. What reports matter most first?
Answer:
- The first thing anyone should see when they log in is a launch screen. This would allow them to perform different actions, such as: 1. Review past performance, where they first see last year's 9-box, and associated answers, and final end of year comments. 2. Continuous tracking, which has two modes, the first being a screen that is safe to share with the employee to track comments from their one-on-one discussions, the second is the manager view only that has the ability to update scores for the potential questionnaire, or a tentative, year-to-date performance score. 3. And IT admin panel to administer the application 4. HR related activities, such as adding/archiving employees, or manage messages, or review employee details. 5. launch a reiew cycle, which triggers the approval cycle and propts the manager to input one final and complete set of scores for performance and potential.

## Q26. Do you want a visual 9-box matrix with drill-down into employees?
Answer:
- a visual 9-box per employee as a part of the employee profile. Future versions may include department, or companywide 9-box statistics, for high-level evaluation.
 
## Q27. Should reports export to CSV or PDF?
Answer:
- PDF

## Q28. Should there be dashboard summaries by org/team?
Answer:
- Probably not a dashboard, but maybe a message center? Something that makes the comment system more intuitive? this idea needs to be fleshed out more.

---

# 4G. Future SaaS possibility

## Q29. Do you want the architecture shaped so tenant separation would be easier later?
Answer:
- For future versions, yes.

## Q30. Do you want to keep that out of v1 entirely to reduce complexity?
Answer:
- Yes.

## 5. Suggested initial v1 scope

This is a recommended starting point only.
