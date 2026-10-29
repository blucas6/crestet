
- decouple light layer from display
    - light layer is a cosmetic, displayer just changes the color when rendering
    - mental map should be an object, it can hold the entitylayer and a light layer
    - the displayer should accept a mental map object from the brain component
    - then it can display based on that
- rewrite color pair module to be dynamic
    - store pairs in a dictionary
    - each entity saves a fg and bg instead of a color
