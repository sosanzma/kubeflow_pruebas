from kfp import dsl

@dsl.component(base_image='sosanzma/preprocess:latest')
def preprocess_data() -> str:
    return '/output/processed.csv'

@dsl.pipeline(
    name='simple-preprocessing-pipeline',
    description='Lee un CSV y hace preprocesamiento con pandas'
)
def preprocessing_pipeline():
    preprocess_task = preprocess_data()
    preprocess_task.set_display_name('Preprocess Data')
