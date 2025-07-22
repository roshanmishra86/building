Preparation - You will needed to this 

1. An OpenAI api key 
2. Google OAuth Client with credentials set up
3. recall.ai API key (for meeting bot)
4. A copy of this sheet `https://docs.google.com/spreadsheets/d/14BvEzVVxExSyqQaNibzQVZy2v5YcDqLDZR8T3b4gVh8/copy`
5. In this sheet the ID is `14BvEzVVxExSyqQaNibzQVZy2v5YcDqLDZR8T3b4gVh8` you should find out the id for the new set.

To set up this workflow follow these steps

1. Download the `meeting_workflow.json` file module2
2. Upload it to your n8n workflow place 
3. Add openai API keys in the OpenAI nodes 
4. SheetID when asked
5. the sheet within the google sheet also has ID but you can manually fetch them 
6. Run the web hook like in the video 


# feature work needed
1. Meta prompting 
2. Formatting text data the same way as the node 
3. By pass the openAI 25 mb size limit with chunking 


to reduce the audio file size minimize bit rate