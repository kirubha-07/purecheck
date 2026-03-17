import os
import pandas as pd
from django.core.management import execute_from_command_line
from django.conf import settings


def export_complaints_to_csv():
    """
    Export all complaints from database to CSV for model retraining.
    Creates a file at: ml/saved_models/training_data.csv
    """
    try:
        from core.models import Complaint
        
        # Fetch all complaints
        complaints = Complaint.objects.all().values(
            'id',
            'source',
            'city',
            'state',
            'food_item',
            'adulterant',
            'severity',
            'created_at'
        )
        
        df = pd.DataFrame(list(complaints))
        
        # Create output directory
        output_dir = os.path.join(
            os.path.dirname(__file__),
            'saved_models'
        )
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to CSV
        output_path = os.path.join(output_dir, 'training_data.csv')
        df.to_csv(output_path, index=False)
        
        print(f"✓ Exported {len(df)} complaints to {output_path}")
        return output_path
    
    except ImportError:
        print("Error: Django not configured. Run this as a Django command or from manage.py shell")
        return None
    except Exception as e:
        print(f"Error exporting complaints: {e}")
        return None


if __name__ == '__main__':
    export_complaints_to_csv()
