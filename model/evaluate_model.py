from .recommendation_model import RecommendationModel

from sklearn.model_selection import KFold

class Evaluate:
    def __init__(self, users, products, interactions):
        self.interactions = interactions
        self.users = users
        self.products = products
        self.model = RecommendationModel(users, products, interactions)
        num_recommendations = 5
        k = 5
        num_splits = 5
        kf = KFold(n_splits=num_splits)
        user_ids = self.interactions['userId'].unique()

        self.result = ''

        for fold_idx, (_, test_index) in enumerate(kf.split(user_ids)):
            print(f"Fold {fold_idx + 1} / {num_splits}")
            test_users = user_ids[test_index][:10]
            
            avg_precision, avg_recall, avg_f1_score = self._evaluate_recommendation_system(
                test_users, num_recommendations, k
            )

            self.result += f"Average Metrics:\nPrecision@{k}: {avg_precision:.4f}\nRecall@{k}: {avg_recall:.4f}\nF1 Score: {avg_f1_score:.4f}\n============================================\n"
            
            print("Average Metrics:")
            print(f"Precision@{k}: {avg_precision:.4f}")
            print(f"Recall@{k}: {avg_recall:.4f}")
            print(f"F1 Score: {avg_f1_score:.4f}")
            print("=" * 40)

    
    def _get_interacted_product_ids(self, user_id):
        return self.interactions[
            self.interactions['userId'] == user_id
            ]['productId'].tolist()

    def _get_preferred_product_ids(self, user_id):
        user_interests = self.users.loc[
            self.users['_id'] == user_id, 'preferences'].iloc[0]
        preferred = self.products[
            self.products.category.isin(user_interests)]
        return preferred['_id']

    def _calculate_metrics(self, recommended_products, interacted_products, popular_products, k):
        intersection = set(
            recommended_products
            ).intersection(
            set(interacted_products)
            ).union(set(popular_products[:k]))
        
        precision = len(intersection) / (2 * k)  # Divide by 2*k since both interacted and popular products are included
        recall = len(intersection) / len(interacted_products)
        f1_score = (2 * precision * recall) / (
            precision + recall
            ) if (precision + recall) > 0 else 0
        
        return precision, recall, f1_score

    def _evaluate_recommendation_system(self, user_ids, num_recommendations=5, k=5):
        avg_precision = 0
        avg_recall = 0
        avg_f1_score = 0
        
        for user_id in user_ids:
            user_recs = self.model.recommendations(
                user_id, num_recommendations)
            interacted_products = self._get_interacted_product_ids(user_id)
            preferred_products = self._get_preferred_product_ids(user_id)
            
            recommended_products = user_recs['_id'].tolist()
            precision, recall, f1_score = self._calculate_metrics(recommended_products, interacted_products, preferred_products, k)
            
            avg_precision += precision
            avg_recall += recall
            avg_f1_score += f1_score
        
        num_users = len(user_ids)
        avg_precision /= num_users
        avg_recall /= num_users
        avg_f1_score /= num_users
        
        return avg_precision, avg_recall, avg_f1_score

# print(Evaluate())
