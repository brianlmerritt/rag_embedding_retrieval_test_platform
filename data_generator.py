import json
import uuid
import random

# Sample veterinary content data
courses = [
    {"id": "VET101", "name": "Small Animal Medicine"},
    {"id": "VET102", "name": "Large Animal Medicine"},
    {"id": "VET201", "name": "Veterinary Surgery"},
    {"id": "VET301", "name": "Diagnostic Imaging"}
]

activities = [
    {"id": "ACT101", "name": "Renal Diseases", "strand": "Internal Medicine"},
    {"id": "ACT102", "name": "Cardiac Diseases", "strand": "Internal Medicine"},
    {"id": "ACT103", "name": "Gastrointestinal Disorders", "strand": "Internal Medicine"},
    {"id": "ACT201", "name": "Soft Tissue Surgery", "strand": "Surgery"},
    {"id": "ACT202", "name": "Orthopedic Surgery", "strand": "Surgery"},
    {"id": "ACT301", "name": "Radiography Techniques", "strand": "Diagnostics"},
    {"id": "ACT302", "name": "Ultrasonography", "strand": "Diagnostics"}
]

# Sample content snippets for each activity
content_snippets = {
    "ACT101": [
        "Chronic Kidney Disease (CKD) in cats is a progressive deterioration of renal function over time. Treatment goals include managing symptoms, slowing progression, and improving quality of life.",
        "Dietary management is crucial for CKD in cats. Prescription renal diets contain reduced protein, phosphorus, and sodium while providing adequate calories and increasing B-vitamins.",
        "Fluid therapy is essential for cats with CKD to maintain hydration. Subcutaneous fluids may be administered at home by owners after proper training.",
        "Medications for CKD in cats may include phosphate binders, potassium supplements, anti-hypertensives, and erythropoietin for anemia.",
        "Regular monitoring of CKD includes blood work (BUN, creatinine, phosphorus, potassium), urinalysis, blood pressure, and body weight assessment."
    ],
    "ACT102": [
        "Hypertrophic cardiomyopathy (HCM) is the most common cardiac disease in cats, characterized by thickening of the left ventricular wall and interventricular septum.",
        "Diagnosis of cardiac disease in small animals often requires echocardiography, ECG, radiography, and cardiac biomarkers like NT-proBNP.",
        "Treatment for congestive heart failure includes diuretics (furosemide), ACE inhibitors, pimobendan, and potentially beta-blockers or calcium channel blockers.",
        "Mitral valve disease is the most common cardiac disorder in small breed dogs, particularly in older patients."
    ],
    "ACT103": [
        "Canine parvovirus is a highly contagious viral disease affecting the gastrointestinal tract of dogs, characterized by severe vomiting and hemorrhagic diarrhea.",
        "Treatment of acute pancreatitis in dogs and cats involves aggressive fluid therapy, pain management, anti-emetics, and nutritional support.",
        "Inflammatory Bowel Disease (IBD) in cats can be managed through dietary modification, antibiotics such as metronidazole, and immunosuppressive drugs in severe cases."
    ],
    "ACT201": [
        "Surgical site infections are a significant concern in veterinary surgery. Proper aseptic technique and perioperative antibiotics help minimize this risk.",
        "The principles of wound healing include inflammation, proliferation, and remodeling phases. Understanding these processes helps guide appropriate wound management.",
        "Proper instrument handling and suture techniques are fundamental skills for any veterinary surgeon. Materials selection depends on the tissue type and location."
    ],
    "ACT202": [
        "Cranial cruciate ligament rupture is one of the most common orthopedic injuries in dogs. Surgical options include extracapsular repair, TPLO, and TTA procedures.",
        "Management of fractures requires consideration of biomechanical forces and appropriate fixation methods, including external fixators, plates, screws, or intramedullary pins.",
        "Hip dysplasia is a common developmental orthopedic disease in large breed dogs. Treatment options range from conservative management to total hip replacement."
    ]
}

def generate_sample_data(num_documents=50):
    """Generate sample veterinary learning content data"""
    documents = []
    
    for i in range(num_documents):
        # Randomly select a course and activity
        course = random.choice(courses)
        activity = random.choice(activities)
        
        # Get content snippets for this activity (or use generic if none available)
        content_list = content_snippets.get(activity["id"], ["Generic veterinary content for study and reference."])
        
        # Randomly select 1-3 content snippets and combine them
        num_snippets = min(random.randint(1, 3), len(content_list))
        selected_snippets = random.sample(content_list, num_snippets)
        content = " ".join(selected_snippets)
        
        # Create document
        doc = {
            "id": str(uuid.uuid4()),
            "contents": content,
            "course_id": course["id"],
            "course_name": course["name"],
            "activity_id": activity["id"],
            "activity_name": activity["name"],
            "strand": activity["strand"]
        }
        
        documents.append(doc)
    
    return documents

def save_sample_data(output_path="./data/vet_moodle_dataset.jsonl", num_documents=50):
    """Generate and save sample data to JSONL file"""
    documents = generate_sample_data(num_documents)
    
    # Ensure directory exists
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write to JSONL file
    with open(output_path, 'w') as f:
        for doc in documents:
            f.write(json.dumps(doc) + '\n')
    
    print(f"Generated {num_documents} sample documents and saved to {output_path}")

if __name__ == "__main__":
    save_sample_data(num_documents=100)