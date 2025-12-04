# Add Training Modules - Management Command Guide

## Overview

This management command adds training modules with video URLs to the training database.

## Usage

### Basic Usage (Dry Run - Preview Only)

```bash
python manage.py add_training_modules --dry-run
```

This will show what would be created without actually creating anything.

### Create Training Modules

```bash
python manage.py add_training_modules
```

This will create or update the training modules.

### Clear Existing and Recreate

```bash
python manage.py add_training_modules --clear
```

This will delete existing modules with matching titles before creating new ones.

## Training Modules Added

The script adds the following training modules:

### English Modules (Order 1-6)

1. **Module 1** - Financial Literacy Module 1 - Introduction to Personal Finance
   - Video: `https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+1_HD1080.mp4`
   - Order: 1
   - Score: 10.0

2. **Module 2** - Financial Literacy Module 2 - Understanding Savings and Investments
   - Video: `https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+2_HD1080.mp4`
   - Order: 2
   - Score: 10.0

3. **Module 3** - Financial Literacy Module 3 - Banking and Financial Services
   - Video: `https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+3_HD1080+.mp4`
   - Order: 3
   - Score: 10.0

4. **Module 4** - Financial Literacy Module 4 - Insurance and Protection
   - Video: `https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+4_HD1080.mp4`
   - Order: 4
   - Score: 10.0

5. **Module 5** - Financial Literacy Module 5 - Credit and Loans
   - Video: `https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+5_HD1080.mp4`
   - Order: 5
   - Score: 10.0

6. **Module 6** - Financial Literacy Module 6 - Financial Planning and Budgeting
   - Video: `https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+6_HD1080.mp4`
   - Order: 6
   - Score: 10.0

### Tamil Module

7. **Module 1 (Tamil)** - Financial Literacy Module 1 - Introduction to Personal Finance (Tamil)
   - Language: Tamil (ta)
   - Video: `https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+1_HD1080_Tamil.mp4`
   - Order: 7
   - Score: 10.0

### Additional Module

8. **What is a Savings Account** - Learn about savings accounts and how they work
   - Video: `https://finmitratraining.s3.ap-south-1.amazonaws.com/What_is_a_Savings_Account_.mp4`
   - Order: 8
   - Score: 10.0

## Features

- **Automatic Detection**: If a module with the same title and language already exists, it will be updated instead of creating a duplicate
- **Content Type**: Automatically set to "video" since all modules have video URLs
- **Active Status**: All modules are set to `is_active=True` by default
- **Ordering**: Modules are ordered sequentially (1-8)

## Example Output

```
✓ Created: Module 1 (en)
✓ Created: Module 2 (en)
✓ Created: Module 3 (en)
✓ Created: Module 4 (en)
✓ Created: Module 5 (en)
✓ Created: Module 6 (en)
✓ Created: Module 1 (Tamil) (ta)
✓ Created: What is a Savings Account (en)

============================================================
Summary:
  Created: 8
  Updated: 0
  Total modules: 8
============================================================
```

## Updating Modules

If you need to update a module (e.g., change video URL or description), you can:

1. **Edit the script** (`training/management/commands/add_training_modules.py`) and modify the module data
2. **Run the command again** - it will automatically update existing modules

Or use the Django admin interface at `/admin/training/trainingsection/`

## Adding Questions

After creating the modules, you can add questions using:

1. **Django Admin**: Navigate to each training section and add questions inline
2. **API**: Use the bulk questions API endpoint
3. **Management Command**: Create a separate command to add questions (similar to `seed_mixed_sections.py`)

## Verification

After running the command, verify the modules were created:

```bash
# Using Django shell
python manage.py shell
>>> from training.models import TrainingSection
>>> TrainingSection.objects.filter(is_active=True).count()
8
>>> TrainingSection.objects.all().values_list('title', 'language', 'order')
```

Or check via the API:

```bash
curl --location 'http://localhost:8000/api/training/sections/' \
--header 'Authorization: Bearer YOUR_TOKEN'
```

## Notes

- All modules are created with `content_type='video'` since they have video URLs
- The script handles URL encoding (spaces are encoded as `+` in the URLs)
- Modules are ordered sequentially for proper display in the app
- Each module has a default score of 10.0 points

