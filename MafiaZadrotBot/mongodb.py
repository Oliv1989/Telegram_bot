from pymongo import MongoClient
from settings import MONGO_DB, MONGODB_LINK

mdb = MongoClient(MONGODB_LINK)[MONGO_DB]

def search_or_save_user(mdb, effective_user, message):
    user = mdb.users.find_one({'user_id': effective_user.id}) #поиск в коллекции user по user.id
    if not user:
        user = {
            'user_id': effective_user.id,
            'first_name': effective_user.first_name,
            'last_name': effective_user.last_name,
            'chat_id': message.chat.id
        }
        mdb.users.insert_one(user)
    return user

def save_user_form(mdb, user, user_data):
    mdb.users.update_one(
        {'_id': user['_id']},
        {'$set': {'form': {'name': user_data['name'],
                           'age': user_data['age'],
                           'evaluation': user_data['evaluation'],
                           'comment': user_data['comment']}}}
    )
    return user