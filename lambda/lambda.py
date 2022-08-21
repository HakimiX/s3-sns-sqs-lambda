def handler(event, context):
  print("received event: {}".format(event))
  return {
    "statusCode": 200,
    "body": "success"
  }