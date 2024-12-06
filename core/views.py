from django.shortcuts import render
from google.cloud import bigquery
from .chatbot import ChatBot
from .analyzebot import AnalyzeBot
from main_file.settings import CLIENT, API_KEY
import json, requests
import pandas as pd
from bs4 import BeautifulSoup
from django.http import HttpResponseBadRequest

def about(request):
    return render(request, 'about.html')


# Create your views here.
def gemcloud_view(request):
    chatbot = ChatBot(api_key=API_KEY)
    chatbot.start_conversation()
    context = {}
    file_path = "core/templates/data_file.csv"
    
    if request.method == 'POST':
        user_input = request.POST.get('message')
        
        try:
            gemini_answer = chatbot.send_prompt(user_input)
            response = json.loads(gemini_answer)
            
        except SyntaxError as s:
            return HttpResponseBadRequest(f"On 33 Syntax error: {s}")
        
        if response[0] == 1:
            sql_query = response[1].replace('```sql', '').replace('```', '').strip()
            
            try:
                query_job = CLIENT.query(
                    query=sql_query, 
                    location='US', 
                    job_config=bigquery.QueryJobConfig(maximum_bytes_billed=1634520268800),
                    job_id_prefix='job__hacker_news_posts',
                )
                
                with open(file_path, 'w') as file:
                    file.write('')
                df = query_job.to_dataframe()
                dict_data = df.to_dict(orient='records')
                
                # Convert dictionary to DataFrame
                df.to_csv(file_path, index=False)
                
                context['response'] = sql_query
                context['dict_data'] = dict_data
            
            except Exception as e:
                analysis = f"Something went wrong while fetching the data: {e}"
                return render(request, 'index.html', context={"response": sql_query, "analysis": analysis})
        
        if response[0] == 2:
            analyzebot = AnalyzeBot(api_key=API_KEY)
            analyzebot.start_conversation()
            post_id = response[1]
            df_loaded = pd.read_csv(file_path)
            dict_data = df_loaded.to_dict(orient='records')
            try:
                url = df_loaded[df_loaded['id'] == post_id]['url'].values[0]
                text = df_loaded[df_loaded['id'] == post_id]['text'].values[0]
                
                if url is None:
                    response = "URL not found for the provided post ID."
                    return render(request, 'index.html', context={"response": response, "dict_data": dict_data})
                
                # Send the GET request to the URL
                try:
                    response = requests.get(url)
                    response.raise_for_status()  # Raise an exception for HTTP errors
                except requests.exceptions.RequestException as e:
                    if text:
                        analysis = analyzebot.send_prompt(text)
                        return render(request, 'index.html', context={"analysis": analysis})
                    else:
                        response = "This Post no longer exist! please try other post for analysis"
                        return render(request, 'index.html', context={"response": response, "dict_data": dict_data})
                
                
                response_content = response.text
                
                def remove_html_tags(response_content):
                    soup = BeautifulSoup(response_content, 'html.parser')
                    return soup.get_text()
                
                clean_data = remove_html_tags(response_content)
                analysis = analyzebot.send_prompt(clean_data)
                context['analysis'] = analysis
                return render(request, 'index.html', context={"analysis": analysis})
            
            except Exception as e:
                response = "Data not found for the provided post ID. Please try some other post for analysis"
                return render(request, 'index.html', context={"response": response, "dict_data": dict_data})

            
        return render(request, 'index.html', context=context)
    else:
        return render(request,'index.html')
