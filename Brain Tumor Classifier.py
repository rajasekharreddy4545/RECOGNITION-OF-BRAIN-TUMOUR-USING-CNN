from imutils import paths
import matplotlib.pyplot as plt
import argparse
import os
import cv2

# Load the images directories
path = "brain_tumor_dataset"
image_paths = list(paths.list_images(path))

images = []
labels = []

for image_path in image_paths:
    label = image_path.split(os.path.sep)[-2]
    image = cv2.imread(image_path)
    image = cv2.resize(image, (224, 224))
    images.append(image)
    labels.append(label)

def plot_image(image):
    plt.imshow(image)
    plt.show()

plot_image(images[0])



from sklearn.preprocessing import LabelBinarizer
from tensorflow.keras.utils import to_categorical
import numpy as np

images = np.array(images) / 255.0
labels = np.array(labels)

label_binarizer = LabelBinarizer()
labels = label_binarizer.fit_transform(labels)
labels = to_categorical(labels)

(train_X, test_X, train_Y, test_Y) = train_test_split(images, labels, test_size=0.10, random_state=42, stratify=labels)

train_generator = ImageDataGenerator(fill_mode='nearest', rotation_range=15)

base_model = VGG16(weights='imagenet', input_tensor=Input(shape=(224, 224, 3)), include_top=False)
base_input = base_model.input

base_output = base_model.output
base_output = AveragePooling2D(pool_size=(4, 4))(base_output)
base_output = Flatten(name="flatten")(base_output)
base_output = Dense(64, activation="relu")(base_output)
base_output = Dropout(0.5)(base_output)
base_output = Dense(2, activation="softmax")(base_output)

for layer in base_model.layers:
    layer.trainable = False

model = Model(inputs=base_input, outputs=base_output)
model.compile(optimizer=Adam(learning_rate=1e-3), metrics=['accuracy'], loss='binary_crossentropy')

print(model.summary())

batch_size = 8
train_steps = len(train_X) // batch_size
validation_steps = len(test_X) // batch_size
epochs = 30

history = model.fit(train_generator.flow(train_X, train_Y, batch_size=batch_size),
                    steps_per_epoch=train_steps,
                    validation_data=(test_X, test_Y),
                    validation_steps=validation_steps,
                    epochs=epochs)

predictions = model.predict(test_X, batch_size=batch_size)
predictions = np.argmax(predictions, axis=1)
actuals = np.argmax(test_Y, axis=1)

print(classification_report(actuals, predictions, target_names=label_binarizer.classes_))

cm = confusion_matrix(actuals, predictions)
print(cm)

total = sum(sum(cm))
accuracy = (cm[0, 0] + cm[1, 1]) / total
print("Accuracy: {:.4f}".format(accuracy))

N = epochs
plt.style.use("ggplot")
plt.figure()
plt.plot(np.arange(0, N), history.history["loss"], label="train_loss")
plt.plot(np.arange(0, N), history.history["val_loss"], label="val_loss")
plt.plot(np.arange(0, N), history.history["acc"], label="train_acc")
plt.plot(np.arange(0, N), history.history["val_acc"], label="val_acc")

plt.title("Training Loss and Accuracy on Brain Dataset")
plt.xlabel("Epoch")
plt.ylabel("Loss / Accuracy")
plt.legend(loc="lower left")
plt.savefig("plot.jpg")
plt.show()

# Save the trained model
model.save("brain_tumor_detection_model.h5")

# Save label binarizer
with open("label_binarizer.pkl", "wb") as f:
    pickle.dump(label_binarizer, f)


