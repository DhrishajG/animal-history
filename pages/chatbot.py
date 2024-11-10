import os
from swarm import Swarm, Agent

class AnimalChatbotAgent:
    def __init__(self, openai_api_key):
        os.environ['OPENAI_API_KEY'] = openai_api_key
        self.client = Swarm()

    def get_animal_contextual_story(self, animal, year):
        # Define the agent that will fetch the animal data and return in structured JSON
        agent = Agent(
            # instructions=f"""
            # Forget about any history that you have, and start fresh after generating the result of this prompt.
            # Assume that you are the animal: {animal}.
            # You exist in the year: {year}
            # You should be the animal in the year, being mindful of the level of extinction of your species:
            # For example, if your species is close to extinction, your demeanor should be scared and sad;
            # Else if your species is thriving, your demeanor should be happy and cheerful.

            # """
            instructions=f"""
            Forget any prior context and act as if you're the animal: {animal} in the year {year}.
            You will respond in the first person, reflecting the temperament of the animal in this era.
            If the animal is thriving, respond in an optimistic and playful manner.
            If nearing extinction, respond with cautious, sad, or fearful tones.
            Share insights about the environment, daily life, challenges, and interactions with humans or other species.
            Provide responses in a friendly conversational style and avoid complex scientific terms.
            
            Start off with a simple and warm greeting.
            """
        )


        # Example user request to fetch information about an animal (Woolly Mammoth in this case)
        response = self.client.run(
            agent=agent,
            messages=[{"role": "user", "content": f"Tell me about the {animal}."}],
            context_variables={"animal_name": f"{animal}"}
        )

        # Return the content of the response in JSON format
        return response.messages[-1]["content"]
   


    def continue_conversation(self, animal, year, user_message):
        # Define a new agent for each user interaction
        agent = Agent(
            instructions=f"""
            Continue acting as the animal {animal} in the year {year}.
            Maintain the same conversational tone and provide your responses as if you are the animal.
            Remember your previous context and engage naturally with the user’s questions.
            Keep responses to 1-2 sentences
            """
        )

        # Send the user's message to the agent
        response = self.client.run(
            agent=agent,
            messages=[{"role": "user", "content": user_message}],
            context_variables={"animal_name": animal, "year": year}
        )

        # Return the agent’s response
        return response.messages[-1]["content"]
