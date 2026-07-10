def calculate_bmi(weight, height):
    """
    Calculate BMI (Body Mass Index).
    weight: float (kg)
    height: float (cm)
    Returns: tuple (bmi_value, category)
    """
    if not weight or not height or height <= 0:
        return 0.0, "Unknown"
    
    height_m = height / 100.0
    bmi = weight / (height_m ** 2)
    bmi = round(bmi, 1)
    
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25.0:
        category = "Normal"
    elif bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"
        
    return bmi, category


def calculate_bmr(weight, height, age, gender):
    """
    Calculate BMR (Basal Metabolic Rate) using Mifflin-St Jeor equation.
    weight: float (kg)
    height: float (cm)
    age: int
    gender: str ('Male', 'Female', 'Other')
    """
    if not weight or not height or not age:
        return 0.0
        
    # Mifflin-St Jeor
    if gender == 'Male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    elif gender == 'Female':
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else: # Other / default average
        bmr = 10 * weight + 6.25 * height - 5 * age - 78
        
    return round(bmr, 0)


def calculate_tdee(bmr, activity_level):
    """
    Calculate TDEE (Total Daily Energy Expenditure).
    bmr: float
    activity_level: str
    """
    multipliers = {
        'Sedentary': 1.2,          # Little or no exercise
        'Lightly Active': 1.375,   # Light exercise/sports 1-3 days/week
        'Moderately Active': 1.55, # Moderate exercise/sports 3-5 days/week
        'Very Active': 1.725,      # Hard exercise/sports 6-7 days/week
        'Extra Active': 1.9        # Very hard exercise/sports & physical job or 2x training
    }
    
    multiplier = multipliers.get(activity_level, 1.2)
    return round(bmr * multiplier, 0)


def calculate_calorie_target(tdee, fitness_goal):
    """
    Calculate daily calorie target based on goal.
    tdee: float
    fitness_goal: str
    """
    if not tdee:
        return 0.0
        
    # Caloric adjustments
    if fitness_goal == 'Weight Loss':
        # 500 kcal deficit (standard weight loss deficit of 0.5 kg/week)
        target = tdee - 500
        # Ensure it doesn't go below safety limits (1200 for women, 1500 for men usually, let's keep it safe at 1200 minimum)
        if target < 1200:
            target = 1200
    elif fitness_goal == 'Muscle Gain':
        # 300 kcal surplus for lean bulking
        target = tdee + 300
    elif fitness_goal == 'Strength':
        # Small surplus of 100 kcal or maintenance
        target = tdee + 150
    elif fitness_goal == 'Endurance':
        # Maintenance plus carbohydrate considerations (usually maintenance is fine for general calculation)
        target = tdee
    else: # General Fitness / Maintenance
        target = tdee
        
    return round(target, 0)


def calculate_water_target(weight, activity_level):
    """
    Calculate recommended daily water intake in ml.
    weight: float (kg)
    activity_level: str
    """
    if not weight:
        return 2500.0 # Default
        
    # Base: 35 ml water per kg of body weight
    base_water = weight * 35.0
    
    # Adjust for activity level (active people sweat more and need more water)
    adjustments = {
        'Sedentary': 0.0,
        'Lightly Active': 250.0,
        'Moderately Active': 500.0,
        'Very Active': 750.0,
        'Extra Active': 1000.0
    }
    
    extra = adjustments.get(activity_level, 0.0)
    total_water = base_water + extra
    
    # Round to nearest 50ml, keep within standard limits [1500ml, 5000ml]
    total_water = round(total_water / 50.0) * 50.0
    return max(1500.0, min(total_water, 5000.0))
