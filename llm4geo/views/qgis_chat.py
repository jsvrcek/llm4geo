import json

import jsonschema
from django.conf import settings
from django.http import JsonResponse
from jsonschema.exceptions import ValidationError
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from rest_framework.views import APIView

from llm4geo.schemas.qgis_project_description import get_qgis_project_description
from llm4geo.schemas.supported_functions import get_supported_functions, get_function_schema, get_function_name_schema
from llm4geo.serializers import QGISSerializer


class QGISChatView(APIView):
    supported_functions = get_supported_functions()
    function_name_schema = get_function_name_schema()

    def get_function_name(self, text, chat_history=None):
        system = f"You are a chatbot trying to help the user choose a custom function to call which will execute some actions within QGIS.  The user will give you some information and you will pick from a list of supported functions: {json.dumps(self.supported_functions)}"
        prompt = ChatPromptTemplate.from_messages([SystemMessage(content=system), MessagesPlaceholder("chat_history"), ("human", "{input}")])
        model = settings.LLM_MODEL(model=settings.OPENAI_MODEL, openai_api_key=settings.OPENAI_API_KEY)
        structured_llm = model.with_structured_output(self.function_name_schema)
        structured_llm_with_prompt = prompt | structured_llm
        response = structured_llm_with_prompt.invoke({"chat_history": chat_history, "input": text})
        function_name = response['function_name']
        retries = 2
        while function_name not in self.supported_functions and retries:
            print(f"Got invalid function {function_name} retying...")
            text_input = f"You chose the function_name {function_name} which is not in the list of available functions {list(self.supported_functions.keys())}.  Given the previous prompt"
            response = structured_llm_with_prompt.invoke({"chat_history": chat_history, "input": text_input})
            function_name = response['function_name']
            retries -= 1
        return response

    def get_function(self, function_name, text, project_description, chat_history=None):
        function_schema = get_function_schema(function_name, project_description)
        system = f"Using {function_schema} and the users current project which uses a schema of: \n\n {get_qgis_project_description()} and the users project specifically uses: \n\n {project_description} using use that description to help."
        prompt = ChatPromptTemplate.from_messages([SystemMessage(content=system), MessagesPlaceholder("chat_history"), ("human", "{input}")])
        model = settings.LLM_MODEL(model=settings.OPENAI_MODEL, openai_api_key=settings.OPENAI_API_KEY)
        structured_llm = model.with_structured_output(function_schema)
        structured_llm_with_prompt = prompt | structured_llm
        try:
            response = structured_llm_with_prompt.invoke({"chat_history": chat_history, "input": text})
            retries = 2
            while retries:
                try:
                    jsonschema.validate(response, function_schema)
                    break
                except ValidationError as e:
                    if not retries:
                        raise e

                    print(f"Got invalid params {response} for function {function_name}: {e}")
                    print(f"Retrying {retries} time(s).")
                    text_input = f"You chose the params {response} which does not match {function_schema} and gives the following error: {e}.  Given the previous prompt: '{text}' provide a response that matches the schema."
                    response = structured_llm_with_prompt.invoke({"chat_history": chat_history, "input": text_input})
                
        except Exception as e:
            print(f"Failed to get_function with schema {json.dumps(function_schema)}")
            raise e
        return response

    def post(self, request):
        serializer = QGISSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        text_input = serializer.validated_data['text_input']
        project_description = serializer.validated_data['project_description']
        chat_history = serializer.validated_data['chat_history']
        function_name_response = self.get_function_name(text_input, chat_history)
        function_name = function_name_response['function_name']
        # Check if we need to get more information about the function (i.e. it needs params) or just skip that and pass it back.
        if "properties" not in self.supported_functions[function_name]:
            function_response = {}
        else:
            function_response = self.get_function(function_name, text_input, project_description, chat_history)
        return JsonResponse({"chat": function_name_response['chat'], "function_name": function_name,
                             "parameters": function_response})
