# nlp-assignment-04-ollama

1. In the 'nlp-assignment-04-ollama-newBranch\webscraper' folder, run 'python crawler.py' after downloading and connecting to MongoDB. This will store data of CSUF domain names in MongoDB.

2. In 'nlp-assignment-04-ollama-newBranch' folder, run 'python populate_database.py' to get stored information from MongoDB and downloaded PDFs, seperate them to chunks, vector embed them, 
    and store them in ChromaDB.

3. In 'nlp-assignment-04-ollama-newBranch' folder, run 'python query_data.py' to interact with the ChatBot that has knowledge of CSUF resources! :^) 

    to quit the chatbot, either CTRL+C or type "quit".
