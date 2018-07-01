import pymongo

def main():
    celeblist = []

    cli = pymongo.MongoClient()
    db = cli.interview_details
    f = open("celebdata/conan/2016.txt", "r")
    f1 = f.readlines()
    for x in f1:
        celebdict = {}
        if x == "\n":
            continue
        x = x.replace("\n","")
        celebdict['name'] = x
        celeblist.append(celebdict)
        #print(x)
    print(celeblist)
    db.celebrity_collection.insert_many(celeblist)

if __name__ == "__main__":
    main()
