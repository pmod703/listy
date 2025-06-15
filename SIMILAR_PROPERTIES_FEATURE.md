# Similar Property Criteria Feature

## Overview

The Similar Property Criteria feature allows real estate agents to define their perception of what constitutes a "similar property" when analyzing competition for open home scheduling. This provides more accurate and relevant competition analysis.

## How It Works

### Frontend Interface

The new feature adds a dedicated section in the property details form with three dropdown selectors:

1. **Similar Bedrooms** - Define bedroom criteria for competing properties
2. **Similar Bathrooms** - Define bathroom criteria for competing properties  
3. **Similar Car Spaces** - Define car space criteria for competing properties

### Available Options

Each selector supports multiple criteria types:

#### Exact Values
- "Exactly 1", "Exactly 2", "Exactly 3", etc.

#### Ranges
- "1-2 bedrooms", "2-3 bedrooms", "3-4 bedrooms", etc.
- "1-2 bathrooms", "2-3 bathrooms", etc.
- "0-1 spaces", "1-2 spaces", "2-3 spaces", etc.

#### Minimum Values (Plus)
- "2+ bedrooms", "3+ bedrooms", "4+ bedrooms", etc.
- "1+ bathrooms", "2+ bathrooms", etc.
- "1+ spaces", "2+ spaces", etc.

## Use Cases

### Example 1: Selling a 4-Bedroom Family Home
If you're selling a 4-bedroom house, you might set:
- **Similar Bedrooms**: "3-5 bedrooms" (buyers looking at 4BR might also consider 3BR or 5BR)
- **Similar Bathrooms**: "2+ bathrooms" (minimum expectation for family homes)
- **Similar Car Spaces**: "1-3 spaces" (typical range for family properties)

### Example 2: Selling a 1-Bedroom Apartment
For a 1-bedroom apartment, you might set:
- **Similar Bedrooms**: "1-2 bedrooms" (studio/1BR buyers might consider 2BR)
- **Similar Bathrooms**: "1 bathroom" (exact match for apartments)
- **Similar Car Spaces**: "0-1 spaces" (many apartments have no parking)

### Example 3: Selling a Luxury Property
For a high-end 5-bedroom home, you might set:
- **Similar Bedrooms**: "4+ bedrooms" (luxury buyers want space)
- **Similar Bathrooms**: "3+ bathrooms" (luxury expectation)
- **Similar Car Spaces**: "2+ spaces" (luxury properties typically have multiple car spaces)

## Technical Implementation

### Backend Processing

1. **Parameter Parsing**: The API receives similar property criteria as URL parameters
2. **Criteria Parsing**: Custom functions parse criteria strings like "3-4", "2+", "1" into min/max values
3. **Property Filtering**: Inspections are filtered based on simulated property details that match the criteria
4. **Competition Analysis**: Only similar properties are counted in the competition analysis

### API Parameters

The following new parameters are added to the `/api/inspections` endpoint:

- `similar_bedrooms` - Bedroom criteria (e.g., "3-4", "2+", "3")
- `similar_bathrooms` - Bathroom criteria (e.g., "2+", "1-2", "2")
- `similar_car_spots` - Car space criteria (e.g., "1-2", "0+", "1")

### Response Data

The API response now includes:

```json
{
  "total_inspections": 15,
  "similar_inspections": 8,
  "search_params": {
    "similar_property_criteria": {
      "bedrooms": "3-4",
      "bathrooms": "2+", 
      "car_spots": "1-2"
    }
  }
}
```

## Benefits

1. **More Accurate Competition Analysis**: Only count properties that are actually competing for the same buyer pool
2. **Better Time Recommendations**: Recommendations are based on relevant competition, not all properties
3. **Agent Expertise**: Allows agents to apply their market knowledge and buyer behavior insights
4. **Flexible Criteria**: Support for exact matches, ranges, and minimum values to handle various scenarios

## Future Enhancements

1. **Property Type Filtering**: Add property type criteria (house, apartment, townhouse)
2. **Price Range Integration**: Include price brackets in similarity criteria
3. **Machine Learning**: Use historical data to suggest optimal similarity criteria
4. **Advanced Parsing**: Support more complex criteria like "2-3 OR 4+" bedrooms
5. **Real Property Data**: Extract actual property details from listings instead of simulation

## Testing

Use the included test script to verify functionality:

```bash
python test_similar_properties.py
```

This will test various criteria combinations and display the filtering results.