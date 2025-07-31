#!/usr/bin/env python3
"""
Discover All Tables Script
Tries to query all possible table names to discover what exists in the database
"""

import os
from typing import Dict, List, Any
from pathlib import Path
from dotenv import load_dotenv

# Database connection
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️  Supabase not installed. Run: pip install supabase")


class TableDiscoverer:
    def __init__(self):
        """Initialize the table discoverer"""
        load_dotenv()

        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')

        if SUPABASE_AVAILABLE and self.supabase_url and self.supabase_key:
            try:
                self.supabase = create_client(
                    self.supabase_url, self.supabase_key)
                print("✅ Connected to Supabase")
            except Exception as e:
                print(f"❌ Failed to connect to Supabase: {e}")
                self.supabase = None
        else:
            self.supabase = None
            print("⚠️  Supabase not configured or not available")

    def discover_tables(self) -> Dict[str, Dict[str, Any]]:
        """Discover all tables by trying to query them"""
        if not self.supabase:
            return {}

        # Comprehensive list of possible table names
        possible_tables = [
            # Known tables from previous analysis
            'systems', 'component_specifications', 'product_images',

            # Common table patterns
            'images', 'extracted_images', 'products', 'components', 'specifications',
            'system_components', 'product_specifications', 'image_metadata',
            'catalog_data', 'flexlink_systems', 'flexlink_components',
            'system_summaries', 'component_data', 'product_data',
            'catalog_images', 'extracted_data', 'system_data',

            # Additional possible tables
            'users', 'user_data', 'user_profiles', 'user_settings',
            'sessions', 'auth', 'authentication', 'login_data',
            'logs', 'log_data', 'activity_logs', 'system_logs',
            'files', 'file_data', 'documents', 'document_data',
            'uploads', 'upload_data', 'media', 'media_data',
            'content', 'content_data', 'pages', 'page_data',
            'settings', 'configuration', 'config', 'config_data',
            'metadata', 'meta_data', 'info', 'information',
            'stats', 'statistics', 'analytics', 'analytics_data',
            'reports', 'report_data', 'exports', 'export_data',
            'imports', 'import_data', 'backups', 'backup_data',
            'cache', 'cache_data', 'temp', 'temporary', 'temp_data',
            'archive', 'archived', 'archive_data', 'old_data',
            'legacy', 'legacy_data', 'historical', 'history',
            'audit', 'audit_logs', 'audit_trail', 'audit_data',
            'permissions', 'roles', 'role_data', 'access_control',
            'notifications', 'notification_data', 'messages', 'message_data',
            'comments', 'comment_data', 'feedback', 'feedback_data',
            'ratings', 'rating_data', 'reviews', 'review_data',
            'bookmarks', 'bookmark_data', 'favorites', 'favorite_data',
            'subscriptions', 'subscription_data', 'memberships', 'membership_data',
            'orders', 'order_data', 'transactions', 'transaction_data',
            'payments', 'payment_data', 'billing', 'billing_data',
            'invoices', 'invoice_data', 'receipts', 'receipt_data',
            'categories', 'category_data', 'tags', 'tag_data',
            'labels', 'label_data', 'groups', 'group_data',
            'teams', 'team_data', 'organizations', 'organization_data',
            'companies', 'company_data', 'clients', 'client_data',
            'customers', 'customer_data', 'vendors', 'vendor_data',
            'suppliers', 'supplier_data', 'partners', 'partner_data',
            'contacts', 'contact_data', 'addresses', 'address_data',
            'locations', 'location_data', 'sites', 'site_data',
            'projects', 'project_data', 'tasks', 'task_data',
            'jobs', 'job_data', 'workflows', 'workflow_data',
            'processes', 'process_data', 'pipelines', 'pipeline_data',
            'queues', 'queue_data', 'jobs_queue', 'job_queue',
            'schedules', 'schedule_data', 'events', 'event_data',
            'calendars', 'calendar_data', 'appointments', 'appointment_data',
            'meetings', 'meeting_data', 'conferences', 'conference_data',
            'webinars', 'webinar_data', 'seminars', 'seminar_data',
            'trainings', 'training_data', 'courses', 'course_data',
            'lessons', 'lesson_data', 'modules', 'module_data',
            'assignments', 'assignment_data', 'homework', 'homework_data',
            'exams', 'exam_data', 'tests', 'test_data',
            'quizzes', 'quiz_data', 'surveys', 'survey_data',
            'polls', 'poll_data', 'votes', 'vote_data',
            'elections', 'election_data', 'campaigns', 'campaign_data',
            'marketing', 'marketing_data', 'advertising', 'advertising_data',
            'promotions', 'promotion_data', 'discounts', 'discount_data',
            'coupons', 'coupon_data', 'vouchers', 'voucher_data',
            'gift_cards', 'gift_card_data', 'loyalty', 'loyalty_data',
            'rewards', 'reward_data', 'points', 'point_data',
            'credits', 'credit_data', 'balances', 'balance_data',
            'accounts', 'account_data', 'wallets', 'wallet_data',
            'portfolios', 'portfolio_data', 'investments', 'investment_data',
            'stocks', 'stock_data', 'bonds', 'bond_data',
            'mutual_funds', 'mutual_fund_data', 'etfs', 'etf_data',
            'currencies', 'currency_data', 'exchange_rates', 'exchange_rate_data',
            'markets', 'market_data', 'trading', 'trading_data',
            'orders_trading', 'trading_orders', 'positions', 'position_data',
            'holdings', 'holding_data', 'allocations', 'allocation_data',
            'diversification', 'diversification_data', 'risk', 'risk_data',
            'volatility', 'volatility_data', 'performance', 'performance_data',
            'returns', 'return_data', 'yields', 'yield_data',
            'dividends', 'dividend_data', 'interest', 'interest_data',
            'capital_gains', 'capital_gain_data', 'losses', 'loss_data',
            'profits', 'profit_data', 'revenue', 'revenue_data',
            'income', 'income_data', 'expenses', 'expense_data',
            'costs', 'cost_data', 'budgets', 'budget_data',
            'forecasts', 'forecast_data', 'projections', 'projection_data',
            'plans', 'plan_data', 'strategies', 'strategy_data',
            'goals', 'goal_data', 'objectives', 'objective_data',
            'targets', 'target_data', 'milestones', 'milestone_data',
            'deadlines', 'deadline_data', 'timelines', 'timeline_data',
            'schedules_project', 'project_schedules', 'gantt', 'gantt_data',
            'kanban', 'kanban_data', 'scrum', 'scrum_data',
            'agile', 'agile_data', 'waterfall', 'waterfall_data',
            'sprints', 'sprint_data', 'iterations', 'iteration_data',
            'releases', 'release_data', 'versions', 'version_data',
            'builds', 'build_data', 'deployments', 'deployment_data',
            'environments', 'environment_data', 'servers', 'server_data',
            'hosts', 'host_data', 'domains', 'domain_data',
            'urls', 'url_data', 'links', 'link_data',
            'redirects', 'redirect_data', 'aliases', 'alias_data',
            'shortcuts', 'shortcut_data', 'bookmarks_web', 'web_bookmarks',
            'favorites_web', 'web_favorites', 'history_web', 'web_history',
            'cookies', 'cookie_data', 'sessions_web', 'web_sessions',
            'tracking', 'tracking_data', 'analytics_web', 'web_analytics',
            'metrics', 'metric_data', 'kpis', 'kpi_data',
            'dashboards', 'dashboard_data', 'widgets', 'widget_data',
            'charts', 'chart_data', 'graphs', 'graph_data',
            'visualizations', 'visualization_data', 'reports_analytics', 'analytics_reports',
            'insights', 'insight_data', 'trends', 'trend_data',
            'patterns', 'pattern_data', 'anomalies', 'anomaly_data',
            'outliers', 'outlier_data', 'correlations', 'correlation_data',
            'regressions', 'regression_data', 'predictions', 'prediction_data',
            'forecasts_ml', 'ml_forecasts', 'models', 'model_data',
            'algorithms', 'algorithm_data', 'ml_models', 'machine_learning_models',
            'ai_models', 'artificial_intelligence_models', 'neural_networks', 'neural_network_data',
            'deep_learning', 'deep_learning_data', 'nlp', 'nlp_data',
            'text_analysis', 'text_analysis_data', 'sentiment', 'sentiment_data',
            'emotions', 'emotion_data', 'mood', 'mood_data',
            'personality', 'personality_data', 'behavior', 'behavior_data',
            'preferences', 'preference_data', 'interests', 'interest_data',
            'hobbies', 'hobby_data', 'skills', 'skill_data',
            'expertise', 'expertise_data', 'experience', 'experience_data',
            'qualifications', 'qualification_data', 'certifications', 'certification_data',
            'licenses', 'license_data', 'accreditations', 'accreditation_data',
            'degrees', 'degree_data', 'diplomas', 'diploma_data',
            'certificates', 'certificate_data', 'awards', 'award_data',
            'achievements', 'achievement_data', 'honors', 'honor_data',
            'recognition', 'recognition_data', 'commendations', 'commendation_data',
            'testimonials', 'testimonial_data', 'endorsements', 'endorsement_data',
            'references', 'reference_data', 'recommendations', 'recommendation_data',
            'referrals', 'referral_data', 'networks', 'network_data',
            'connections', 'connection_data', 'relationships', 'relationship_data',
            'friendships', 'friendship_data', 'followers', 'follower_data',
            'following', 'following_data', 'subscribers', 'subscriber_data',
            'subscriptions_content', 'content_subscriptions', 'members', 'member_data',
            'participants', 'participant_data', 'attendees', 'attendee_data',
            'guests', 'guest_data', 'visitors', 'visitor_data',
            'viewers', 'viewer_data', 'listeners', 'listener_data',
            'readers', 'reader_data', 'authors', 'author_data',
            'writers', 'writer_data', 'editors', 'editor_data',
            'publishers', 'publisher_data', 'contributors', 'contributor_data',
            'creators', 'creator_data', 'artists', 'artist_data',
            'designers', 'designer_data', 'developers', 'developer_data',
            'programmers', 'programmer_data', 'engineers', 'engineer_data',
            'architects', 'architect_data', 'consultants', 'consultant_data',
            'advisors', 'advisor_data', 'mentors', 'mentor_data',
            'coaches', 'coach_data', 'trainers', 'trainer_data',
            'instructors', 'instructor_data', 'teachers', 'teacher_data',
            'professors', 'professor_data', 'lecturers', 'lecturer_data',
            'speakers', 'speaker_data', 'presenters', 'presenter_data',
            'moderators', 'moderator_data', 'facilitators', 'facilitator_data',
            'hosts_event', 'event_hosts', 'organizers', 'organizer_data',
            'coordinators', 'coordinator_data', 'managers', 'manager_data',
            'supervisors', 'supervisor_data', 'leaders', 'leader_data',
            'directors', 'director_data', 'executives', 'executive_data',
            'officers', 'officer_data', 'administrators', 'administrator_data',
            'moderators_system', 'system_moderators', 'curators', 'curator_data',
            'editors_content', 'content_editors', 'reviewers', 'reviewer_data',
            'approvers', 'approver_data', 'validators', 'validator_data',
            'verifiers', 'verifier_data', 'auditors', 'auditor_data',
            'inspectors', 'inspector_data', 'examiners', 'examiner_data',
            'assessors', 'assessor_data', 'evaluators', 'evaluator_data',
            'judges', 'judge_data', 'arbitrators', 'arbitrator_data',
            'mediators', 'mediator_data', 'negotiators', 'negotiator_data',
            'brokers', 'broker_data', 'agents', 'agent_data',
            'representatives', 'representative_data', 'advocates', 'advocate_data',
            'lawyers', 'lawyer_data', 'attorneys', 'attorney_data',
            'counselors', 'counselor_data', 'therapists', 'therapist_data',
            'psychologists', 'psychologist_data', 'psychiatrists', 'psychiatrist_data',
            'doctors', 'doctor_data', 'physicians', 'physician_data',
            'nurses', 'nurse_data', 'paramedics', 'paramedic_data',
            'technicians', 'technician_data', 'specialists', 'specialist_data',
            'experts', 'expert_data', 'professionals', 'professional_data',
            'practitioners', 'practitioner_data', 'operators', 'operator_data',
            'handlers', 'handler_data', 'controllers', 'controller_data',
            'monitors', 'monitor_data', 'observers', 'observer_data',
            'watchers', 'watcher_data', 'guards', 'guard_data',
            'security', 'security_data', 'protectors', 'protector_data',
            'defenders', 'defender_data', 'fighters', 'fighter_data',
            'warriors', 'warrior_data', 'soldiers', 'soldier_data',
            'officers_military', 'military_officers', 'generals', 'general_data',
            'commanders', 'commander_data', 'captains', 'captain_data',
            'lieutenants', 'lieutenant_data', 'sergeants', 'sergeant_data',
            'corporals', 'corporal_data', 'privates', 'private_data',
            'recruits', 'recruit_data', 'cadets', 'cadet_data',
            'trainees', 'trainee_data', 'apprentices', 'apprentice_data',
            'interns', 'intern_data', 'volunteers', 'volunteer_data',
            'helpers', 'helper_data', 'assistants', 'assistant_data',
            'aides', 'aide_data', 'supporters', 'supporter_data',
            'sponsors', 'sponsor_data', 'donors', 'donor_data',
            'benefactors', 'benefactor_data', 'patrons', 'patron_data',
            'philanthropists', 'philanthropist_data', 'humanitarians', 'humanitarian_data',
            'activists', 'activist_data', 'advocates_social', 'social_advocates',
            'reformers', 'reformer_data', 'revolutionaries', 'revolutionary_data',
            'pioneers', 'pioneer_data', 'innovators', 'innovator_data',
            'inventors', 'inventor_data', 'discoverers', 'discoverer_data',
            'explorers', 'explorer_data', 'adventurers', 'adventurer_data',
            'travelers', 'traveler_data', 'tourists', 'tourist_data',
            'pilgrims', 'pilgrim_data', 'migrants', 'migrant_data',
            'immigrants', 'immigrant_data', 'refugees', 'refugee_data',
            'asylum_seekers', 'asylum_seeker_data', 'displaced', 'displaced_data',
            'evacuees', 'evacuee_data', 'survivors', 'survivor_data',
            'victims', 'victim_data', 'casualties', 'casualty_data',
            'fatalities', 'fatality_data', 'deaths', 'death_data',
            'births', 'birth_data', 'marriages', 'marriage_data',
            'divorces', 'divorce_data', 'adoptions', 'adoption_data',
            'foster_care', 'foster_care_data', 'guardianship', 'guardianship_data',
            'custody', 'custody_data', 'visitation', 'visitation_data',
            'alimony', 'alimony_data', 'child_support', 'child_support_data',
            'inheritance', 'inheritance_data', 'estates', 'estate_data',
            'wills', 'will_data', 'trusts', 'trust_data',
            'foundations', 'foundation_data', 'charities', 'charity_data',
            'nonprofits', 'nonprofit_data', 'ngos', 'ngo_data',
            'associations', 'association_data', 'societies', 'society_data',
            'clubs', 'club_data', 'groups_social', 'social_groups',
            'communities', 'community_data', 'neighborhoods', 'neighborhood_data',
            'districts', 'district_data', 'wards', 'ward_data',
            'precincts', 'precinct_data', 'constituencies', 'constituency_data',
            'electorates', 'electorate_data', 'voters', 'voter_data',
            'citizens', 'citizen_data', 'residents', 'resident_data',
            'inhabitants', 'inhabitant_data', 'populations', 'population_data',
            'demographics', 'demographic_data', 'census', 'census_data',
            'statistics_population', 'population_statistics', 'vital_statistics', 'vital_statistics_data',
            'birth_rates', 'birth_rate_data', 'death_rates', 'death_rate_data',
            'migration_rates', 'migration_rate_data', 'growth_rates', 'growth_rate_data',
            'fertility_rates', 'fertility_rate_data', 'mortality_rates', 'mortality_rate_data',
            'life_expectancy', 'life_expectancy_data', 'infant_mortality', 'infant_mortality_data',
            'maternal_mortality', 'maternal_mortality_data', 'child_mortality', 'child_mortality_data',
            'adult_mortality', 'adult_mortality_data', 'elderly_mortality', 'elderly_mortality_data',
            'disease_rates', 'disease_rate_data', 'infection_rates', 'infection_rate_data',
            'vaccination_rates', 'vaccination_rate_data', 'immunization_rates', 'immunization_rate_data',
            'health_indicators', 'health_indicator_data', 'wellness_indicators', 'wellness_indicator_data',
            'fitness_indicators', 'fitness_indicator_data', 'nutrition_indicators', 'nutrition_indicator_data',
            'dietary_data', 'diet_data', 'nutrition_data', 'food_data',
            'meals', 'meal_data', 'recipes', 'recipe_data',
            'ingredients', 'ingredient_data', 'nutrients', 'nutrient_data',
            'vitamins', 'vitamin_data', 'minerals', 'mineral_data',
            'proteins', 'protein_data', 'carbohydrates', 'carbohydrate_data',
            'fats', 'fat_data', 'fiber', 'fiber_data',
            'calories', 'calorie_data', 'energy', 'energy_data',
            'metabolism', 'metabolism_data', 'digestion', 'digestion_data',
            'absorption', 'absorption_data', 'excretion', 'excretion_data',
            'elimination', 'elimination_data', 'detoxification', 'detoxification_data',
            'cleansing', 'cleansing_data', 'purification', 'purification_data',
            'filtration', 'filtration_data', 'separation', 'separation_data',
            'extraction', 'extraction_data', 'distillation', 'distillation_data',
            'crystallization', 'crystallization_data', 'precipitation', 'precipitation_data',
            'condensation', 'condensation_data', 'evaporation', 'evaporation_data',
            'sublimation', 'sublimation_data', 'deposition', 'deposition_data',
            'melting', 'melting_data', 'freezing', 'freezing_data',
            'boiling', 'boiling_data', 'solidification', 'solidification_data',
            'liquefaction', 'liquefaction_data', 'gasification', 'gasification_data',
            'combustion', 'combustion_data', 'oxidation', 'oxidation_data',
            'reduction', 'reduction_data', 'hydrolysis', 'hydrolysis_data',
            'dehydration', 'dehydration_data', 'hydration', 'hydration_data',
            'synthesis', 'synthesis_data', 'decomposition', 'decomposition_data',
            'polymerization', 'polymerization_data', 'depolymerization', 'depolymerization_data',
            'crosslinking', 'crosslinking_data', 'branching', 'branching_data',
            'grafting', 'grafting_data', 'blending', 'blending_data',
            'mixing', 'mixing_data', 'stirring', 'stirring_data',
            'shaking', 'shaking_data', 'agitation', 'agitation_data',
            'vibration', 'vibration_data', 'oscillation', 'oscillation_data',
            'rotation', 'rotation_data', 'revolution', 'revolution_data',
            'translation', 'translation_data', 'displacement', 'displacement_data',
            'velocity', 'velocity_data', 'acceleration', 'acceleration_data',
            'momentum', 'momentum_data', 'force', 'force_data',
            'pressure', 'pressure_data', 'stress', 'stress_data',
            'strain', 'strain_data', 'tension', 'tension_data',
            'compression', 'compression_data', 'shear', 'shear_data',
            'torsion', 'torsion_data', 'bending', 'bending_data',
            'deflection', 'deflection_data', 'deformation', 'deformation_data',
            'elasticity', 'elasticity_data', 'plasticity', 'plasticity_data',
            'ductility', 'ductility_data', 'brittleness', 'brittleness_data',
            'hardness', 'hardness_data', 'toughness', 'toughness_data',
            'strength', 'strength_data', 'stiffness', 'stiffness_data',
            'rigidity', 'rigidity_data', 'flexibility', 'flexibility_data',
            'malleability', 'malleability_data', 'conductivity', 'conductivity_data',
            'resistivity', 'resistivity_data', 'permeability', 'permeability_data',
            'porosity', 'porosity_data', 'density', 'density_data',
            'viscosity', 'viscosity_data', 'surface_tension', 'surface_tension_data',
            'adhesion', 'adhesion_data', 'cohesion', 'cohesion_data',
            'friction', 'friction_data', 'lubrication', 'lubrication_data',
            'wear', 'wear_data', 'erosion', 'erosion_data',
            'corrosion', 'corrosion_data', 'rust', 'rust_data',
            'oxidation_metal', 'metal_oxidation', 'reduction_metal', 'metal_reduction',
            'electrolysis', 'electrolysis_data', 'electroplating', 'electroplating_data',
            'anodizing', 'anodizing_data', 'galvanizing', 'galvanizing_data',
            'chromating', 'chromating_data', 'phosphating', 'phosphating_data',
            'nitriding', 'nitriding_data', 'carburizing', 'carburizing_data',
            'heat_treatment', 'heat_treatment_data', 'annealing', 'annealing_data',
            'quenching', 'quenching_data', 'tempering', 'tempering_data',
            'normalizing', 'normalizing_data', 'case_hardening', 'case_hardening_data',
            'surface_hardening', 'surface_hardening_data', 'core_hardening', 'core_hardening_data',
            'through_hardening', 'through_hardening_data', 'selective_hardening', 'selective_hardening_data',
            'differential_hardening', 'differential_hardening_data', 'gradient_hardening', 'gradient_hardening_data',
            'pattern_hardening', 'pattern_hardening_data', 'flame_hardening', 'flame_hardening_data',
            'induction_hardening', 'induction_hardening_data', 'laser_hardening', 'laser_hardening_data',
            'electron_beam_hardening', 'electron_beam_hardening_data', 'plasma_hardening', 'plasma_hardening_data',
            'ion_hardening', 'ion_hardening_data', 'nitrocarburizing', 'nitrocarburizing_data',
            'boronizing', 'boronizing_data', 'sulfonitriding', 'sulfonitriding_data',
            'sulfidizing', 'sulfidizing_data', 'chromizing', 'chromizing_data',
            'aluminizing', 'aluminizing_data', 'siliconizing', 'siliconizing_data',
            'vanadizing', 'vanadizing_data', 'titanizing', 'titanizing_data',
            'zirconizing', 'zirconizing_data', 'hafnizing', 'hafnizing_data',
            'niobizing', 'niobizing_data', 'tantalizing', 'tantalizing_data',
            'molybdenizing', 'molybdenizing_data', 'tungstenizing', 'tungstenizing_data',
            'rhenizing', 'rhenizing_data', 'osmiumizing', 'osmiumizing_data',
            'iridiumizing', 'iridiumizing_data', 'platinumizing', 'platinumizing_data',
            'goldizing', 'goldizing_data', 'silverizing', 'silverizing_data',
            'copperizing', 'copperizing_data', 'nickelizing', 'nickelizing_data',
            'cobaltizing', 'cobaltizing_data', 'ironizing', 'ironizing_data',
            'manganeseizing', 'manganeseizing_data', 'chromiumizing', 'chromiumizing_data',
            'vanadiumizing', 'vanadiumizing_data', 'titaniumizing', 'titaniumizing_data',
            'aluminumizing', 'aluminumizing_data', 'magnesiumizing', 'magnesiumizing_data',
            'berylliumizing', 'berylliumizing_data', 'lithiumizing', 'lithiumizing_data',
            'sodiumizing', 'sodiumizing_data', 'potassiumizing', 'potassiumizing_data',
            'rubidiumizing', 'rubidiumizing_data', 'cesiumizing', 'cesiumizing_data',
            'franciumizing', 'franciumizing_data', 'calciumizing', 'calciumizing_data',
            'strontiumizing', 'strontiumizing_data', 'bariumizing', 'bariumizing_data',
            'radiumizing', 'radiumizing_data', 'scandiumizing', 'scandiumizing_data',
            'yttriumizing', 'yttriumizing_data', 'lanthanumizing', 'lanthanumizing_data',
            'actiniumizing', 'actiniumizing_data', 'thoriumizing', 'thoriumizing_data',
            'protactiniumizing', 'protactiniumizing_data', 'uraniumizing', 'uraniumizing_data',
            'neptuniumizing', 'neptuniumizing_data', 'plutoniumizing', 'plutoniumizing_data',
            'americiumizing', 'americiumizing_data', 'curiumizing', 'curiumizing_data',
            'berkeliumizing', 'berkeliumizing_data', 'californiumizing', 'californiumizing_data',
            'einsteiniumizing', 'einsteiniumizing_data', 'fermiumizing', 'fermiumizing_data',
            'mendeleviumizing', 'mendeleviumizing_data', 'nobeliumizing', 'nobeliumizing_data',
            'lawrenciumizing', 'lawrenciumizing_data', 'rutherfordiumizing', 'rutherfordiumizing_data',
            'dubniumizing', 'dubniumizing_data', 'seaborgiumizing', 'seaborgiumizing_data',
            'bohriumizing', 'bohriumizing_data', 'hassiumizing', 'hassiumizing_data',
            'meitneriumizing', 'meitneriumizing_data', 'darmstadtiumizing', 'darmstadtiumizing_data',
            'roentgeniumizing', 'roentgeniumizing_data', 'coperniciumizing', 'coperniciumizing_data',
            'nihoniumizing', 'nihoniumizing_data', 'fleroviumizing', 'fleroviumizing_data',
            'moscoviumizing', 'moscoviumizing_data', 'livermoriumizing', 'livermoriumizing_data',
            'tennessineizing', 'tennessineizing_data', 'oganessonizing', 'oganessonizing_data'
        ]

        discovered_tables = {}

        print(f"🔍 Testing {len(possible_tables)} possible table names...")

        for i, table_name in enumerate(possible_tables):
            if i % 50 == 0:  # Progress indicator
                print(f"   Progress: {i}/{len(possible_tables)} tables tested")

            try:
                # Try to query the table
                response = self.supabase.table(
                    table_name).select('*').limit(1).execute()

                # If we get here, the table exists
                discovered_tables[table_name] = {
                    'exists': True,
                    'row_count': len(response.data) if response.data else 0,
                    'columns': list(response.data[0].keys()) if response.data else [],
                    'sample_data': response.data[:2] if response.data else []
                }
                print(f"✅ Discovered: {table_name}")

            except Exception as e:
                # Table doesn't exist or error
                error_msg = str(e)
                if "Could not find the table" in error_msg or "does not exist" in error_msg:
                    # Table doesn't exist - this is expected for most tables
                    pass
                else:
                    # Other error - might be a permissions issue or table exists but can't access
                    discovered_tables[table_name] = {
                        'exists': False,
                        'error': error_msg
                    }
                    print(f"⚠️  Error with {table_name}: {error_msg}")

        return discovered_tables

    def generate_discovery_report(self, discovered_tables: Dict[str, Dict[str, Any]]) -> str:
        """Generate a report of discovered tables"""
        report = "# Database Table Discovery Report\n\n"
        report += f"Generated on: {self._get_current_timestamp()}\n\n"

        # Summary
        existing_tables = [
            name for name, data in discovered_tables.items() if data.get('exists', False)]
        error_tables = [name for name, data in discovered_tables.items(
        ) if not data.get('exists', False) and 'error' in data]

        report += "## Summary\n\n"
        report += f"- **Total Tables Tested**: {len(discovered_tables)}\n"
        report += f"- **Existing Tables**: {len(existing_tables)}\n"
        report += f"- **Tables with Errors**: {len(error_tables)}\n"
        report += f"- **Non-existent Tables**: {len(discovered_tables) - len(existing_tables) - len(error_tables)}\n\n"

        # Existing tables
        if existing_tables:
            report += "## Existing Tables\n\n"
            for table_name in sorted(existing_tables):
                data = discovered_tables[table_name]
                report += f"### {table_name}\n"
                report += f"- **Status**: ✅ Exists\n"
                report += f"- **Row Count**: {data.get('row_count', 0)}\n"
                report += f"- **Columns**: {len(data.get('columns', []))}\n"
                if data.get('columns'):
                    report += f"- **Column Names**: {', '.join(data['columns'][:5])}{'...' if len(data['columns']) > 5 else ''}\n"
                report += "\n"

        # Error tables
        if error_tables:
            report += "## Tables with Errors\n\n"
            for table_name in sorted(error_tables):
                data = discovered_tables[table_name]
                report += f"### {table_name}\n"
                report += f"- **Status**: ❌ Error\n"
                report += f"- **Error**: {data.get('error', 'Unknown error')}\n\n"

        return report

    def _get_current_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def run_discovery(self) -> Dict[str, Any]:
        """Run the complete table discovery process"""
        print("🔍 Starting comprehensive table discovery...")

        # Discover all tables
        discovered_tables = self.discover_tables()

        # Generate report
        report = self.generate_discovery_report(discovered_tables)

        # Save report
        report_file = Path("table_discovery_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n✅ Table discovery complete! Report saved to: {report_file}")

        return {
            'timestamp': self._get_current_timestamp(),
            'discovered_tables': discovered_tables,
            'report': report
        }


def main():
    """Main function"""
    discoverer = TableDiscoverer()

    # Run discovery
    results = discoverer.run_discovery()

    # Print summary
    print("\n" + "="*50)
    print("TABLE DISCOVERY SUMMARY")
    print("="*50)

    discovered_tables = results.get('discovered_tables', {})
    existing_tables = [
        name for name, data in discovered_tables.items() if data.get('exists', False)]

    print(f"📊 Total Tables Tested: {len(discovered_tables)}")
    print(f"✅ Existing Tables: {len(existing_tables)}")

    if existing_tables:
        print("\n📋 Found Tables:")
        for table in sorted(existing_tables):
            data = discovered_tables[table]
            print(
                f"  - {table}: {data.get('row_count', 0)} rows, {len(data.get('columns', []))} columns")

    print("="*50)


if __name__ == "__main__":
    main()
