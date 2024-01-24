from openai import OpenAI
from openai._utils import maybe_transform
from openai.types import image_generate_params

client = OpenAI(api_key="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")

response = client.images.generate(
  model="dall-e-2",
  prompt="a white siamese cat",
  size="256x256",
  quality="standard",
  n=1,
)

image_url = response.data[0].url
print(image_url)