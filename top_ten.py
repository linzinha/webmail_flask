import json
import aggregate_email
print("file ran")


def top_counts():
    aggregate_email.aggregate()
    top_senders = []
    # Load JSON data
    with open('static/emails.json') as f:
        data = json.load(f)

    # Create a list of sender-count tuples
    sender_count_tuples = [(sender, count) for sender, count in data["sender"].items()]

    # Sort the list based on the count in descending order
    sender_count_tuples.sort(key=lambda x: x[1], reverse=True)

    # Take the top 10 senders
    top_10_senders = sender_count_tuples[:10]

    # Format the top 10 senders as an HTML list
    for sender, count in top_10_senders:
        top_senders.append({sender: count})

    return top_senders



if __name__ == "__main__":
    top_counts()