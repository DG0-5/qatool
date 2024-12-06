import google.generativeai as genai

class GenAiException(Exception):
    """GenAI Exception Base Class"""

class ChatBot:
    """Chat can only have one candidate count"""
    ChatBot_Name = 'My Gemini AI'
    
    def __init__(self, api_key):
        self.genai = genai
        self.api_key = api_key
        self.genai.configure(api_key=self.api_key)
        self.model = self.genai.GenerativeModel('gemini-pro')
        self.conversation = None
        self._conversation_history = []
        self.preload_conversation()
        
    def send_prompt(self, prompt, temperature=0.8):
        if temperature < 0 or temperature > 1:
            raise GenAiException('Temprature must be between 0 and 1')
        
        if not prompt:
            raise GenAiException('Prompt cannot be empty')
        
        try:
            response = self.conversation.send_message(
                content=prompt, 
                generation_config= self._generation_config(temperature),
            )
            response.resolve()
            return f'{response.text}\n'
        except Exception as e:
            raise GenAiException(str(e))
        
    @property
    def history(self):
        conversation_history = [
            {'role': message.role, 'text': message.parts[0].text} for message in self.conversation.history
        ]
        return conversation_history
    
    def clear_conversation(self):
        self.conversation = self.model.start_chat(history=[])    
    
    def start_conversation(self):
        self.conversation = self.model.start_chat(history=self._conversation_history)
    
    def _generation_config(self, temperature):
        return genai.types.GenerationConfig(temperature=temperature)
        
    def _construct_message(self, text, role='user'):
        return {
            'role': role,
            'parts': text
        }
        
    def preload_conversation(self, conversation_history=None, data=None):
        if isinstance(conversation_history, list):
            self._conversation_history = conversation_history
        else:
            self._conversation_history = [
                self._construct_message(f"""I will provide you with a prompt, and the user will ask questions related to either generating an SQL query or analyzing data based on posts and articles. You need to decide which prompt to use based on the user's question.

                                            Please make sure to format your response as a list. The list should have two values:
                                            If the user asks for an SQL query, the list should be [1, "SQL query"], where 1 indicates a SQL query and the second value is the SQL query string.
                                            If the user requests an analysis of data, the list should be [2, post_id], where 2 indicates data analysis and post_id is an integer provided by the user.

                                            For example:
                                            User Input: "Give me the SQL query for 10 data where the title is 'Google'." Response: [1, "SQL query"]
                                            User Input: "Show me the analysis of post ID 123." Response: [2, 123]

                                            For SQL queries:
                                            Do not provide any data in Obsidian style. Return the SQL query as a plain string only.
                                            This is the example of SQL Query: SELECT * FROM bigquery-public-data.hacker_news.full WHERE title LIKE '%news%' LIMIT 8;, with user-provided conditions included. Always include all columns unless the user specifies specific columns.

                                            Here are the column names and descriptions you need for crafting SQL queries:
                                            title: STRING, Nullable, Story title
                                            url: STRING, Nullable, Story URL
                                            text: STRING, Nullable, Story or comment text
                                            dead: BOOLEAN, Nullable, Is dead?
                                            by: STRING, Nullable, Username of the item's author
                                            score: INTEGER, Nullable, Story score
                                            time: INTEGER, Nullable, Unix time
                                            timestamp: TIMESTAMP, Nullable, Timestamp for the Unix time
                                            type: STRING, Nullable, Type of details (comment, comment_ranking, poll, story, job, pollopt)
                                            id: INTEGER, Nullable, Unique ID of the item
                                            parent: INTEGER, Nullable, Parent comment ID
                                            descendants: INTEGER, Nullable, Number of story or poll descendants
                                            ranking: INTEGER, Nullable, Comment ranking
                                            deleted: BOOLEAN, Nullable, Is deleted?

                                            In the output, the user only wants the query in a single line, with nothing else included.


                """),]
            