export interface StudentRegister {

  id?: number;

  document_type: string;

  document_number: string;

  first_name: string;

  last_name: string;

  full_name?: string;

  date_of_birth: string;

  gender: string;

  grade: string;

  section?: string;

  guardian_name: string;

  guardian_phone: string;

  guardian_email?: string;

  guardian_relationship?: string;

  consent_given: boolean;

  address?: string;

  neighborhood?: string;

  city?: string;

  socioeconomic_stratum?: number;

  is_active: boolean;

  gender_display?: string;

  age?: number;

}