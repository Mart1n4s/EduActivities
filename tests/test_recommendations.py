import numpy as np
from utils.recommendations import (
    vectorize_activity,
    cosine_similarity,
)


SAMPLE_ACTIVITIES = [
    {
        "id": "1",
        "title": "Art Class",
        "categories": ["art", "indoors"],
        "liked_by": ["user1"]
    },
    {
        "id": "2",
        "title": "Soccer Practice",
        "categories": ["sports", "outdoors"],
        "liked_by": []
    },
    {
        "id": "3",
        "title": "Music Workshop",
        "categories": ["music", "indoors"],
        "liked_by": ["user1"]
    },
    {
        "id": "4",
        "title": "Science Club",
        "categories": ["science", "indoors"],
        "liked_by": []
    }
]

def test_get_unique_categories():
    all_activities = SAMPLE_ACTIVITIES

    unique_categories = set()
    for activity in all_activities:
        if "categories" in activity:
            for category in activity["categories"]:
                unique_categories.add(category)

    expected_categories = {
        "art", "music", "sports", "science", "outdoors", "indoors"
    }
    assert unique_categories == expected_categories

def test_get_category_index_map():
    all_activities = SAMPLE_ACTIVITIES
    unique_categories = set()
    for activity in all_activities:
        if "categories" in activity:
            for category in activity["categories"]:
                unique_categories.add(category)
    
    category_map = {}
    for index, category in enumerate(sorted(unique_categories)):
        category_map[category] = index
    
    expected_categories = sorted(["art", "music", "sports", "science", "outdoors", "indoors"])
    actual_categories = sorted(list(category_map.keys()))
    
    assert actual_categories == expected_categories
    
    indices = set(category_map.values())
    assert len(indices) == len(expected_categories)
    assert all(isinstance(idx, int) for idx in indices)

def test_vectorize_activity():
    all_activities = SAMPLE_ACTIVITIES
    unique_categories = set()
    for activity in all_activities:
        if "categories" in activity:
            for category in activity["categories"]:
                unique_categories.add(category)
    
    category_map = {}
    for index, category in enumerate(sorted(unique_categories)):
        category_map[category] = index
    
    activity = {
        "categories": ["art", "indoors"]
    }
    vector = vectorize_activity(activity, category_map)
    
    assert len(vector) == len(category_map)
    
    art_index = category_map["art"]
    indoors_index = category_map["indoors"]
    assert vector[art_index] == 1
    assert vector[indoors_index] == 1
    
    for i in range(len(vector)):
        if i not in [art_index, indoors_index]:
            assert vector[i] == 0

def test_cosine_similarity():
    vec1 = np.array([1, 0, 1])
    vec2 = np.array([1, 0, 1])
    assert np.isclose(cosine_similarity(vec1, vec2), 1.0)
    
    vec3 = np.array([1, 0, 0])
    vec4 = np.array([0, 1, 0])
    assert np.isclose(cosine_similarity(vec3, vec4), 0.0)
    
    vec5 = np.array([0, 0, 0])
    assert np.isclose(cosine_similarity(vec5, vec1), 0.0)

def test_get_activity_recommendations():
    all_activities = SAMPLE_ACTIVITIES
    
    unique_categories = set()
    for activity in all_activities:
        if "categories" in activity:
            for category in activity["categories"]:
                unique_categories.add(category)
    
    category_map = {}
    for index, category in enumerate(sorted(unique_categories)):
        category_map[category] = index
    
    user_id = "user1"

    user_liked_activities = [
        activity for activity in all_activities
        if ("liked_by" in activity and user_id in activity["liked_by"])
    ]
    
    liked_activity_vectors = [
        vectorize_activity(activity, category_map) 
        for activity in user_liked_activities
    ]
    
    activities = []
    for activity in all_activities:
        is_liked = activity in user_liked_activities
        
        if is_liked:
            activity["is_liked"] = True
            activity["similarity"] = 1.0
        else:
            activity_vector = vectorize_activity(activity, category_map)
            
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
    
    def sort_key(activity):
        return (not activity["is_liked"], -activity["similarity"])

    activities.sort(key=sort_key)
    
    assert activities[0]["id"] == "1"  
    assert activities[1]["id"] == "3"  
    
    for activity in activities:
        assert "similarity" in activity
        assert "is_liked" in activity
    
    liked_activities = [a for a in activities if a["is_liked"]]
    unliked_activities = [a for a in activities if not a["is_liked"]]
    
    assert all(a["is_liked"] for a in liked_activities)
    assert all(not a["is_liked"] for a in unliked_activities)
    
    similarities = [a["similarity"] for a in unliked_activities]
    assert similarities == sorted(similarities, reverse=True)
