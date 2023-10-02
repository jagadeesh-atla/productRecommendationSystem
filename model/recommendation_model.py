import pandas

from . import users, products, interactions

import numpy
numpy.random.seed(1024)

import ast

from sklearn.metrics.pairwise import cosine_similarity

from sklearn.preprocessing import MinMaxScaler

class RecommendationModel:
    def __init__(
            self,
            users=users,
            products=products,
            interactions=interactions
            ):
        self.users = users
        self.products = products
        self.interactions = interactions
        self.user_item_matrix = self._create_user_item_matrix()

        scaler = MinMaxScaler()
        self.normalizedMatrix = scaler.fit_transform(
            self.user_item_matrix
        )

        self.itemSimilarity = cosine_similarity(
            self.normalizedMatrix.T
        )
        print('Model Initiated')

    def _create_user_item_matrix(self):
        matrix = self.interactions.pivot_table(
            index='userId',
            columns='productId',
            values='score',
            aggfunc='sum',
            fill_value=0
        )
        return matrix
    
    def collaborative_recommendations(self, userId, n=5):
        try:
            userIdx = self.user_item_matrix.index.get_loc(userId)
        except Exception as e:
            return pandas.DataFrame(columns=self.products.columns)
        
        userVector = self.normalizedMatrix[userIdx]

        relevantProductIdxx = numpy.where(userVector != 0)[0]

        scores = numpy.dot(
            self.itemSimilarity, userVector
        )
        rankedIdxx = numpy.argsort(scores)[::-1]

        interactionsProductsIdxx = numpy.where(self.interactions['userId'] == userId)[0]

        recommendedProductIdxx = [
            index for index in rankedIdxx
            if index not in interactionsProductsIdxx
        ]

        relevantProductIds = self.user_item_matrix.columns[
            relevantProductIdxx
        ]
        recommendedProductIds = self.user_item_matrix.columns[
            recommendedProductIdxx
        ]

        finalRecIds = [
            productId for productId in recommendedProductIds
            if productId in relevantProductIds
        ]

        recs = self.products[
            self.products['_id'].isin(finalRecIds)
        ]

        return recs.head(n) if n >= 1 else recs

    def preference_recommendations(self, userId, n=5):
        userPreferences = self._get_user_preferences(userId)

        # print(userPreferences[0])
        # print(type(userPreferences))

        recsCollab = self.collaborative_recommendations(
            userId, 0
            )
        
        # print(recsCollab)
        print(userPreferences)
        
        relevant = recsCollab.loc[
            recsCollab['category'].isin(userPreferences)
        ]
        
        recs = self.products.loc[
            self.products['_id'].isin(relevant)
        ]

        return recs.head(n) if n > 0 else recs

    def popular_recommendations(self, n=5):
        recs = self.products.sort_values(
            by='popularity', ascending=False, ignore_index=True
        )  
        return recs.head(n) if n > 0 else recs

    def recommendations(self, userId, n=5):
        n = 5 if (n <= 0) else n

        recsPref = self.preference_recommendations(userId, 0)
        recsPopu = self.popular_recommendations(0)

        userPreferences = self._get_user_preferences(userId)

        recsPopu = recsPopu[
            recsPopu['category'].isin(userPreferences)
        ].sort_values(by='popularity', ascending=False)

        recsClab = self.collaborative_recommendations(userId, 0)

        noPref = int(n * 2 * 0.6) + 1
        noPopu = int(n * 2 * 0.2) + 1
        noClab = int(n * 2 * 0.2) + 1

        cutsPref = recsPref.head(noPref)
        cutsPopu = recsPopu.head(noPopu)
        cutsClab = recsClab.head(noClab)

        recs = pandas.concat(
            [cutsPref, cutsPopu, cutsClab],
            ignore_index=True
        )
        
        return recs.head(n) if n > 0 else recs

    def _get_user_preferences(self, userId):
        userPreferences = self.users.loc[
            self.users['_id'] == userId, 'preferences'
        ].iloc[0]

        return userPreferences
    
    def retrain(self, new_users=None, new_products=None, new_interactions=None):
        if new_users is not None:
            user_df = pandas.DataFrame(new_users)
            user_df['_id'] = user_df['_id'].astype('string')
            self.users = self.users._append(user_df)
        if new_products is not None:
            product_df = pandas.DataFrame(new_products)
            self.products = self.products._append(product_df)
            product_df['_id'] = product_df['_id'].astype('string')

        if new_interactions is not None:
            interaction_df = pandas.DataFrame(new_interactions)
            self.interactions = self.interactions._append(interaction_df)
            interaction_df['userId'] = interaction_df['userId'].astype('string')
            interaction_df['productId'] = interaction_df['productId'].astype('string')

        # Recreate user-item matrix and recompute item similarity
        self.user_item_matrix = self._create_user_item_matrix()
        scaler = MinMaxScaler()
        self.normalizedMatrix = scaler.fit_transform(self.user_item_matrix)
        self.itemSimilarity = cosine_similarity(self.normalizedMatrix.T)

        print('Model Retrained')
        return True

# x = RecommendationModel()

# x.retrain(
#     new_users=[{
#         'userId': 1234567890,
#         'userName': 'admin',
#         'password': 'passWORD',
#         'preferences': [
#             'books',
#             'testing'
#         ]
#     }]
# )

# print(x.recommendations(1234567890, 10))
