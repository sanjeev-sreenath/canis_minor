import pymongo
import sys

if __name__ == "__main__":
    cli = pymongo.MongoClient()
    db = cli.interview_details
    db.hosts.insert_one({
        'name': sys.argv[1],
        'channels': [{
            'youtube_channel_id': sys.argv[2]
        }]
    })
