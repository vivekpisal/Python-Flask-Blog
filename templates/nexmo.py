import nexmo

client = nexmo.Client(key='dfa342c5', secret='Opk33nM0WvyvAODq')

client.send_message({
    'from': 'Nexmo',
    'to': '919359896029',
    'text': 'Hello from Nexmo',
})