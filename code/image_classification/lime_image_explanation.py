import random
from re import X

import numpy as np
import pandas as pd
from keras.applications import inception_v3 as inc_net
from keras.models import load_model

from lime import lime_image
from matplotlib import pyplot as plt

from image_classification_core.dataset_processing.image_dataset_1_processing import get_dataset_1
from image_classification_core.dataset_processing.image_dataset_2_processing import get_dataset_2
from image_classification_core.dataset_processing.image_dataset_3_processing import get_dataset_3

from skimage import transform

###############################
# EXTRACTING LIME EXPLANATION #
###############################
def extracting_lime_explanation(model, generator, save_path):
        # Message 
        print('This may take a few minutes...')
        X_test, y_test = generator.next()

        X_test_processed = [inc_net.preprocess_input(img) for img in X_test]

        def predict_fn(x):
            pred_list = model.predict(x)
            pred_list_final = []
            for index in range(len(pred_list)):
                prediction = pred_list[index][0]
                if prediction > 0.5:
                    pred_list_final.append(np.insert(pred_list[index], 0, (1-prediction)))
                else: 
                    pred_list_final.append(np.insert(pred_list[index], 1, (prediction*-1)))
            pred_list_final = np.array(pred_list_final)
            return pred_list_final

        # Create explainer 
        explainer = lime_image.LimeImageExplainer(verbose=False)
        from skimage.segmentation import mark_boundaries  
        random_indexes = random.sample(range(1,len(X_test)),5)

        for index in random_indexes:
            # Set up the explainer
            explanation = explainer.explain_instance(X_test[index].astype(np.float), predict_fn, top_labels = 2, hide_color = 0, num_samples = 1000)
            print("triggered")
            labels = list(generator.class_indices)
            print(labels)
            preds = model.predict(np.expand_dims(X_test[index], axis=0))
            print("MODEL PREDICTION: ", preds)
            preds = predict_fn(np.expand_dims(X_test[index], axis=0))
            print("COMBINED PREDICTION: ", preds)
            print("ARGMAX:", np.argmax(preds[0]))
            class_pred_1 = int(np.where(np.argmax(preds[0]) ==1, 1,0))
            class_pred_2 = int(np.where(np.argmax(preds[0])==1, 0,1))
            print("CLASS PREDICTION 1 : ", class_pred_1)
            print("CLASS PREDICTION 2 : ", class_pred_2)

            # create figure
            fig = plt.figure(figsize=(10, 7))
            fig.suptitle('Classifier result: {}'.format(labels[class_pred_1]))
                    
            # setting values to rows and column variables
            rows = 2
            columns = 4

            temp, mask = explanation.get_image_and_mask(class_pred_1, positive_only=True , num_features=5, hide_rest=False)

            # Adds a subplot at the 1st position
            fig.add_subplot(rows, columns, 1)
                
            # showing image
            plt.imshow(X_test_processed[index])
            plt.rc('axes', titlesize=8) 
            plt.axis('off')
            plt.title('Original Image')
                
            # Adds a subplot at the 2nd position
            fig.add_subplot(rows, columns, 2)
                
            # showing image
            plt.imshow(mark_boundaries(temp, mask))
            plt.rc('axes', titlesize=8)
            plt.axis('off')
            plt.title('Positive Regions for {}'.format(labels[class_pred_1]))
                
            temp, mask = explanation.get_image_and_mask(class_pred_1, positive_only=False, num_features=10, hide_rest=False)
            # Adds a subplot at the 3rd position
            fig.add_subplot(rows, columns, 3)
                
            # showing image
            plt.imshow(mark_boundaries(temp, mask))
            plt.rc('axes', titlesize=8)
            plt.axis('off')
            plt.title('Positive & Negative Regions for {}'.format(labels[class_pred_1]))

            temp, mask = explanation.get_image_and_mask(class_pred_2, positive_only=True , num_features=5, hide_rest=False)

            # Adds a subplot at the 1st position
            fig.add_subplot(rows, columns, 4)
                
            # showing image
            plt.imshow(X_test_processed[index])
            plt.rc('axes', titlesize=8)
            plt.axis('off')
            plt.title('Original Image')
                
            # Adds a subplot at the 2nd position
            fig.add_subplot(rows, columns, 5)
                
            # showing image
            plt.imshow(mark_boundaries(temp, mask))
            plt.rc('axes', titlesize=8)
            plt.axis('off')
            plt.title('Positive Regions for {}'.format(labels[class_pred_2]))
                
            temp, mask = explanation.get_image_and_mask(class_pred_2, positive_only=False, num_features=10, hide_rest=False)
            # Adds a subplot at the 3rd position
            fig.add_subplot(rows, columns, 6)
                
            # showing image
            plt.imshow(mark_boundaries(temp, mask))
            plt.rc('axes', titlesize=8)
            plt.axis('off')
            plt.title('Positive & Negative Regions for {}'.format(labels[class_pred_2]))

            transformed_img = transform.rotate(X_test_processed[index], angle=-50, cval=255)
            # Adds a subplot at the 2nd position
            fig.add_subplot(rows, columns, 7)
                
            # showing image
            pred_peturb = model.predict(np.expand_dims(transformed_img,axis=0))
            plt.imshow(transformed_img)
            plt.rc('axes', titlesize=8)
            plt.axis('off')
            plt.title("Peturbed classification: " + str(pred_peturb))

            fig.savefig(save_path+str(labels[class_pred_1])+"_"+str(index)+".jpg")

############################################################
# INITIALISING MODEL & DATA FOR FAKE VS REAL FACES DATASET #
############################################################
train_generator, test_generator, valid_generator = get_dataset_1()
model_name = "lime_xai_image_classification_data_1_ConvNet"
model = load_model("models/image_models/"+model_name+".h5")
save_path = 'image_explanations/lime_image_explanations/image_data_1/'
extracting_lime_explanation(model, valid_generator, save_path)

####################################################
# INITIALISING MODEL & DATA FOR CAT VS DOG DATASET #
####################################################
train_generator, test_generator = get_dataset_2()
model_name = "lime_xai_image_classification_data_2_ConvNet" 
model = load_model("models/image_models/"+model_name+".h5")
save_path = 'image_explanations/lime_image_explanations/image_data_2/'
extracting_lime_explanation(model, test_generator, save_path)

###########################################################
# INITIALISING MODEL & DATA FOR WATERMARK VS NO_WATERMARK #
###########################################################
train_generator, valid_generator = get_dataset_3()
model_name = "lime_xai_image_classification_data_3_ConvNet"
model = load_model("models/image_models/"+model_name+".h5")
save_path = 'image_explanations/lime_image_explanations/image_data_3/'
extracting_lime_explanation(model, valid_generator, save_path)
