# UX Design Documentation

## Project
**TikTok Creator Intelligence Web App**  
Wireframes created in **Figma** to define the first end-to-end user experience.

## Design Intent
The UX was designed for small TikTok creators who need fast insights from comment data without technical friction.  
The flow prioritizes:
- Simple upload-first onboarding
- Clear sentiment and keyword visibility
- Actionable recommendations for next content decisions

## Screen 1 — Upload File
This screen introduces the product and guides users to upload a CSV file containing TikTok comments and video metrics.  
Primary UX decision: keep one clear call-to-action so users can start quickly.

![Upload Screen Wireframe](https://github.com/user-attachments/assets/4a6053ee-c521-4250-94d3-cdc9b1dc38d4)

## Screen 2 — Dashboard Overview
After upload, users land on a high-level dashboard view showing key metrics and sentiment distribution.  
Primary UX decision: surface summary information first so creators can understand audience mood immediately.

![Dashboard Wireframe](https://github.com/user-attachments/assets/e1885191-1942-40d6-9dc9-486dfdb9cefd)

## Screen 3 — Insight Details
This view focuses on deeper insights such as top keywords/themes and audience feedback patterns.  
Primary UX decision: separate detailed analysis from the overview to reduce cognitive load.

![Insights Wireframe](https://github.com/user-attachments/assets/4a425e90-c744-4df8-aa01-d91dcfc8969c)

## Screen 4 — Recommendations
The recommendation screen translates analysis into practical content suggestions creators can act on.  
Primary UX decision: move from “data display” to “decision support” so the tool directly supports content strategy.

![Recommendations Wireframe](https://github.com/user-attachments/assets/ab85a886-433d-4d0e-a776-0cac99545ef0)

## End-to-End UX Flow
1. User uploads TikTok comment data  
2. System processes and summarizes sentiment  
3. User explores keyword/topic insights  
4. User receives content recommendations for next posts

## Notes on Figma Process
- Started with low-fidelity wireframes to validate information hierarchy first
- Designed each screen around one primary user goal
- Kept layout simple to fit Streamlit implementation constraints
- Ensured continuity across screens through consistent structure and progression
