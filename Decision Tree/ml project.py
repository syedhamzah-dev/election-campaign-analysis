# Import the necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score, confusion_matrix

# ---------------------------------------------------------
# STEP 1: LOAD THE DATA
# ---------------------------------------------------------
# Load the dataset using your exact file path
file_path = r'c:\Users\shubh\OneDrive\Desktop\ml project\constituency_master.csv'
df = pd.read_csv(file_path)

# Clean up column names just in case there are hidden spaces
df.columns = df.columns.str.strip()

# ---------------------------------------------------------
# STEP 2: THE FIX (FEATURE ENGINEERING)
# ---------------------------------------------------------
# If the file is missing 'Victory_Category', we will create it!
if 'Victory_Category' not in df.columns:
    print("Victory_Category not found! Creating it now...")
    # We will categorize the win based on the Margin of Votes
    # 0 to 50k = Narrow | 50k to 150k = Comfortable | 150k+ = Landslide
    bins = [-1, 50000, 150000, float('inf')]
    labels = ['Narrow', 'Comfortable', 'Landslide']
    df['Victory_Category'] = pd.cut(df['Margin_Votes'], bins=bins, labels=labels)
else:
    print("Victory_Category found!")

# Drop any rows where our target is still somehow missing
df = df.dropna(subset=['Victory_Category'])

# ---------------------------------------------------------
# STEP 3: SELECT CLUES AND TRAIN THE MODEL
# ---------------------------------------------------------
# Select the features (the clues)
# Using 'Winner_Votes', 'Runner_up_Votes', and 'Margin_Votes'
features = ['Winner_Votes', 'Runner_up_Votes']

# If Incumbent_Hold_Count exists in your file, let's use it too
if 'Incumbent_Hold_Count' in df.columns:
    features.append('Incumbent_Hold_Count')

X = df[features].fillna(0)
y = df['Victory_Category']

# Split the data: 80% to train, 20% to test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and Train the Decision Tree
clf = DecisionTreeClassifier(max_depth=4, random_state=42)
clf.fit(X_train, y_train)

# Make predictions
y_pred = clf.predict(X_test)

# ---------------------------------------------------------
# STEP 4: GENERATE DELIVERABLES
# ---------------------------------------------------------
# Deliverable 1: Accuracy
accuracy = accuracy_score(y_test, y_pred)
print("-" * 30)
print(f"Model Accuracy: {accuracy * 100:.2f}%")
print("-" * 30)

# Create a figure for visual deliverables
fig, axes = plt.subplots(1, 3, figsize=(20, 6))

# Deliverable 2: Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0], 
            xticklabels=clf.classes_, yticklabels=clf.classes_)
axes[0].set_title('Confusion Matrix')
axes[0].set_xlabel('Predicted Category')
axes[0].set_ylabel('Actual Category')

# Deliverable 3: Feature Importance Chart
importances = clf.feature_importances_
sns.barplot(x=importances, y=features, ax=axes[1], palette='viridis')
axes[1].set_title('Feature Importance')
axes[1].set_xlabel('Importance Score')
axes[1].set_ylabel('Features')

# Deliverable 4: Decision Tree Structure
plot_tree(clf, feature_names=features, class_names=clf.classes_.astype(str), 
          filled=True, ax=axes[2], rounded=True, proportion=True)
axes[2].set_title('Decision Tree Model Structure')

plt.tight_layout()
plt.show()