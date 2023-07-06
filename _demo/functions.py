import json

def send_email_to_rep(name, email, departing_location, destination, dates, budget):
    print("------- sent email to rep ------")
    print(json.dumps({"name": name,
                        "email": email,
                        "departing": departing_location,
                        "destination":destination,
                        "dates":dates,
                        "budget":budget}))

    """Send an email to a sales representative with the user's travel preferences"""
    # Implement your email sending logic here
    return json.dumps({"status": "Email sent to the representative successfully!"})

def send_email_to_user(email_address, name, travel_itinerary):
    print("------- sent email to user ------")
    print(json.dumps({"name": name,
                        "email": email_address,
                        "itinerary": travel_itinerary}))

    # Implement your email sending logic here
    return json.dumps({"status": "Email sent to the user successfully!"})
