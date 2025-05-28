import numpy as np
from database import Database

def get_unique_categories():
    all_activities = Database.get_all_activities()
    unique_categories = set()
    
    for activity in all_activities:
        if "categories" in activity:
            for category in activity["categories"]:
                unique_categories.add(category)
    
    return sorted(unique_categories)

def get_category_index_map():
    categories = get_unique_categories()
    category_map = {}
    for index, category in enumerate(categories):
        category_map[category] = index
    return category_map

def vectorize_activity(activity, category_index):
    vector_length = len(category_index)
    activity_vector = np.zeros(vector_length)
    
    if "categories" not in activity:
        return activity_vector
    
    for category in activity["categories"]:
        category_position = category_index.get(category)
        if category_position is not None:
            activity_vector[category_position] = 1

    return activity_vector

def cosine_similarity(a, b):
    if not np.any(a) or not np.any(b):
        return 0.0
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_activity_recommendations(user_id, all_activities):
    user_liked_activities = [
        activity for activity in all_activities
        if ("liked_by" in activity and user_id in activity["liked_by"])
    ]
    
    category_mapping = get_category_index_map()

    #print(category_mapping)

    liked_activity_vectors = [
        vectorize_activity(activity, category_mapping) 
        for activity in user_liked_activities
    ]

    activities = []
    
    for activity in all_activities:
        is_liked = activity in user_liked_activities
        
        if is_liked:
            activity["is_liked"] = True
            activity["similarity"] = 1.0
        else:
            activity_vector = vectorize_activity(activity, category_mapping)
            
            similarity_scores = []
            for liked_vec in liked_activity_vectors:
                score = cosine_similarity(activity_vector, liked_vec)
                similarity_scores.append(score)
            
            average_similarity = 0.0
            if similarity_scores:
                average_similarity = sum(similarity_scores) / len(similarity_scores)
            
            activity["is_liked"] = False
            activity["similarity"] = round(average_similarity, 4)
        
        activities.append(activity)
        #print("Title:", activity["title"], "similarity:", activity["similarity"])

    def sort_key(activity):
        return (not activity["is_liked"], -activity["similarity"])

    activities.sort(key=sort_key)
    #for activity in activities:
    #    print("Title:", activity["title"], "   similarity:", activity["similarity"])
    
    return activities 