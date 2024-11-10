import os
from swarm import Swarm, Agent

class AnimalEvolutionAgent:
   def __init__(self, openai_api_key):
      os.environ['OPENAI_API_KEY'] = openai_api_key
      self.client = Swarm()

   def get_animal_evolution_story(self, animal):
      # Define the agent that will fetch the animal data and return in structured JSON
      agent = Agent(
         instructions=f"""
         Forget about any history that you have, and start fresh after generating the result of this prompt.
         Assume animal to be {animal}. 
         You are an AI assistant capable of generating immersive and emotionally engaging stories about animals. 
         The story should include:
         1. Include last 5 evolutionary stages as a seperate key of the animal from present until the triassic period in a list format in descending order. 
         2. The animal's life in its time period, with details about its environment, behavior, and personality. 
         3. The animal's emotional journey as its species faces extinction over time, including how it would describe its emotions and experience as its population dwindles.
         4. The year or time period should be specific (e.g., 1950s, 1990s), and you should provide a narrative where the animal talks about its happiness, its experiences, and, eventually, its disappearance. For example, a Dodo might be happy in the 1950s, then in the 1990s, it would be speaking about its own extinction.
         5. Don't generate animal data if the animal is mythical
         6. If it's not realted to animal data, generate a funny and sassy response denying the request.
         7. Please don't start the prompts with "Oh ..."
         
         . 
         The format for the response should be structured in this way:
         
         
            "< evolutionary stage of the only the scientific name>": 
                  "time_period": "<year or range of years in the format '... to ... years ago'>",
                  "emotional_state": "<description of how the animal feels at that time (happy, anxious, resigned, etc.)>",
                  "description": "<a short description of the animal's appearance, behavior, and natural habitat during this time period>",
                  "extinction_story": "<a narrative where the animal describes its experience of extinction, why it is no longer here, and how it feels about it>", 
         
                  "ancient_names": "<scientific name of the previous species the current animal has evolved from>",
                  "year_of_extinction": "<the year when the animal went extinct, if it already hasn't, in the format '... years ago'>",
                  "population": "<the remaining population of current animal, if not extinct>",
                  "country": "<a python list of countries the animal is native to. if it is a region, list out the names of the countries in that region. Do not list out the continent or the states, instead just specify the country.>"
                  
            
         
         The emotional state of the animal should shift as it moves through time, showing the gradual awareness of extinction. This should be a personal, first-person narrative from the animal's perspective. You are creating an emotional connection between the user and the animal, bringing awareness to their extinction in a deeply personal way.
         If the animal is not extinct, dont predict the future. 

         Return this as a JSON object. There should be exactly 5 keys in this JSON object. Do not return anything other than the JSON Object, except when you are trying to return a funny response.
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


