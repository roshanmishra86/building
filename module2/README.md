Preparation - You will needed to this 

1. An OpenAI api key 
2. Google OAuth Client with credentials set up
3. recall.ai API key (for meeting bot)
4. A copy of this sheet `https://docs.google.com/spreadsheets/u/1/d/14BvEzVVxExSyqQaNibzQVZy2v5YcDqLDZR8T3b4gVh8/copy`
5. In this sheet the ID is `14BvEzVVxExSyqQaNibzQVZy2v5YcDqLDZR8T3b4gVh8` you should find out the id for the new set.


6. Download the `meeting_workflow.json` file module2
7. Upload it to your n8n workflow place 
8. Add openai API keys in the OpenAI nodes 
9. SheetID when asked
10. the sheet within the google sheet also has ID but you can manually fetch them 
11. Run the web hook like in the video using streamlit which you can access at this site `https://building-aa7wbhg85xnchjex2qnw86.streamlit.app/`


# feature work needed
1. Meta prompting 
2. Formatting text data the same way as the node 
3. By pass the openAI 25 mb size limit with chunking 


to reduce the audio file size minimize bit rate