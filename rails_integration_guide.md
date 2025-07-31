# Rails Integration Guide for FlexLink Database Changes

## Overview
This guide helps integrate the new database structure into your Rails application that uses the same Supabase database.

## Database Changes Summary

### New Tables
1. **`systems`** - Main system information (NEW)
2. **`components`** - Component details (RENAMED from component_specifications)
3. **`product_images`** - Image data (EXISTING, enhanced)

### Archived Tables
1. **`archived_components`** - Old components table
2. **`archived_conveyor_systems`** - Old conveyor systems table

## Rails Model Updates

### 1. System Model
```ruby
# app/models/system.rb
class System < ApplicationRecord
  self.table_name = 'systems'
  
  # Associations
  has_many :components, foreign_key: 'system_code', primary_key: 'system_code'
  has_many :product_images, foreign_key: 'system_code', primary_key: 'system_code'
  
  # Validations
  validates :system_code, presence: true, uniqueness: true
  validates :system_name, presence: true
  
  # Scopes
  scope :by_category, ->(category) { where(category: category) }
  scope :by_load_capacity, ->(capacity) { where('load_capacity ILIKE ?', "%#{capacity}%") }
  scope :light_duty, -> { where('load_capacity ILIKE ?', '%light%') }
  scope :medium_duty, -> { where('load_capacity ILIKE ?', '%medium%') }
  scope :heavy_duty, -> { where('load_capacity ILIKE ?', '%heavy%') }
  
  # Instance methods
  def load_score
    case load_capacity&.downcase
    when /light/ then 1
    when /medium/ then 2
    when /heavy/ then 3
    else 1
    end
  end
  
  def compatible_systems
    System.where.not(system_code: system_code)
          .where(category: category)
          .where('load_capacity ILIKE ?', "%#{load_capacity}%")
  end
  
  def applications_list
    applications&.join(', ') || 'N/A'
  end
  
  def key_features_list
    key_features&.join(', ') || 'N/A'
  end
end
```

### 2. Component Model
```ruby
# app/models/component.rb
class Component < ApplicationRecord
  self.table_name = 'components'
  
  # Associations
  belongs_to :system, foreign_key: 'system_code', primary_key: 'system_code'
  
  # Validations
  validates :system_code, presence: true
  validates :component_type, presence: true
  validates :name, presence: true
  
  # Scopes
  scope :by_type, ->(type) { where(component_type: type) }
  scope :for_system, ->(system_code) { where(system_code: system_code) }
  
  # Instance methods
  def specifications_hash
    specifications.is_a?(Hash) ? specifications : {}
  end
  
  def compatibility_list
    compatibility&.join(', ') || 'N/A'
  end
end
```

### 3. ProductImage Model
```ruby
# app/models/product_image.rb
class ProductImage < ApplicationRecord
  self.table_name = 'product_images'
  
  # Associations
  belongs_to :system, foreign_key: 'system_code', primary_key: 'system_code', optional: true
  
  # Scopes
  scope :for_system, ->(system_code) { where(system_code: system_code) }
  scope :with_metadata, -> { where.not(metadata: nil) }
  
  # Instance methods
  def image_url
    # Adjust based on your image storage setup
    url || image_data_url
  end
end
```

## Controller Updates

### 1. Systems Controller
```ruby
# app/controllers/systems_controller.rb
class SystemsController < ApplicationController
  def index
    @systems = System.all.order(:system_code)
    
    # Apply filters
    @systems = @systems.by_category(params[:category]) if params[:category].present?
    @systems = @systems.by_load_capacity(params[:load_capacity]) if params[:load_capacity].present?
    @systems = @systems.where('system_name ILIKE ?', "%#{params[:search]}%") if params[:search].present?
    
    respond_to do |format|
      format.html
      format.json { render json: @systems }
    end
  end
  
  def show
    @system = System.find_by(system_code: params[:id])
    @components = @system.components
    @images = @system.product_images
    
    respond_to do |format|
      format.html
      format.json { render json: @system }
    end
  end
  
  def recommendations
    @system = System.find_by(system_code: params[:id])
    @compatible_systems = @system.compatible_systems.limit(5)
    
    render json: {
      system: @system,
      compatible_systems: @compatible_systems,
      performance_score: calculate_performance_score(@system)
    }
  end
  
  private
  
  def calculate_performance_score(system)
    # Implement performance scoring logic
    base_score = 50
    load_bonus = system.load_score * 10
    category_bonus = 15
    base_score + load_bonus + category_bonus
  end
end
```

### 2. Components Controller
```ruby
# app/controllers/components_controller.rb
class ComponentsController < ApplicationController
  def index
    @components = Component.all
    
    # Apply filters
    @components = @components.by_type(params[:type]) if params[:type].present?
    @components = @components.for_system(params[:system_code]) if params[:system_code].present?
    
    respond_to do |format|
      format.html
      format.json { render json: @components }
    end
  end
  
  def for_system
    @system = System.find_by(system_code: params[:system_code])
    @components = @system.components
    
    render json: {
      system: @system,
      components: @components,
      summary: {
        total_components: @components.count,
        component_types: @components.pluck(:component_type).uniq,
        system_code: @system.system_code
      }
    }
  end
end
```

## Routes Updates

```ruby
# config/routes.rb
Rails.application.routes.draw do
  # Systems routes
  resources :systems, only: [:index, :show] do
    member do
      get :recommendations
      get :components
    end
  end
  
  # Components routes
  resources :components, only: [:index, :show] do
    collection do
      get :for_system
    end
  end
  
  # Product images routes
  resources :product_images, only: [:index, :show] do
    collection do
      get :for_system
    end
  end
  
  # API routes
  namespace :api do
    namespace :v1 do
      resources :systems, only: [:index, :show] do
        member do
          get :recommendations
          get :components
        end
      end
      
      resources :components, only: [:index, :show] do
        collection do
          get :for_system
        end
      end
    end
  end
end
```

## Database Migration

### 1. Create Migration for New Structure
```ruby
# db/migrate/YYYYMMDDHHMMSS_update_flexlink_database_structure.rb
class UpdateFlexlinkDatabaseStructure < ActiveRecord::Migration[7.0]
  def up
    # Note: This migration is informational since the database changes
    # were made directly in Supabase. This ensures Rails knows about the structure.
    
    # Update table names in Rails
    rename_table :component_specifications, :components if table_exists?(:component_specifications)
    
    # Add any Rails-specific indexes or constraints
    add_index :systems, :system_code, unique: true if table_exists?(:systems)
    add_index :systems, :category if table_exists?(:systems)
    add_index :components, :system_code if table_exists?(:components)
    add_index :components, :component_type if table_exists?(:components)
  end
  
  def down
    # Revert changes if needed
    rename_table :components, :component_specifications if table_exists?(:components)
  end
end
```

### 2. Update Schema
```ruby
# db/schema.rb (partial update)
ActiveRecord::Schema[7.0].define(version: 2024_01_01_000000) do
  # Systems table
  create_table "systems", force: :cascade do |t|
    t.string "system_code", null: false
    t.string "system_name", null: false
    t.string "category"
    t.text "description"
    t.string "load_capacity"
    t.string "speed_range"
    t.string "precision_level"
    t.string "chain_width"
    t.string "max_load"
    t.string "temperature_range"
    t.integer "page_reference"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["system_code"], name: "index_systems_on_system_code", unique: true
    t.index ["category"], name: "index_systems_on_category"
  end

  # Components table (renamed from component_specifications)
  create_table "components", force: :cascade do |t|
    t.string "system_code", null: false
    t.string "component_type", null: false
    t.string "name", null: false
    t.jsonb "specifications"
    t.string "compatibility"
    t.text "description"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["system_code"], name: "index_components_on_system_code"
    t.index ["component_type"], name: "index_components_on_component_type"
  end

  # Product images table (existing)
  create_table "product_images", force: :cascade do |t|
    t.string "system_code"
    t.string "image_url"
    t.jsonb "metadata"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["system_code"], name: "index_product_images_on_system_code"
  end
end
```

## API Endpoints

### 1. Systems API
```ruby
# GET /api/v1/systems
# Returns all systems with optional filtering
{
  "systems": [
    {
      "system_code": "X45",
      "system_name": "X45 Chain System",
      "category": "Chain Conveyor",
      "load_capacity": "Light duty",
      "speed_range": "Up to 20 m/min",
      "applications": ["Small assembly operations", "Compact production lines"],
      "key_features": ["Compact design", "25.4 mm pitch chain system"]
    }
  ]
}

# GET /api/v1/systems/X45/recommendations
# Returns compatible systems and analysis
{
  "system": { ... },
  "compatible_systems": [ ... ],
  "performance_score": 85,
  "recommendation": "Good system diversity!"
}
```

### 2. Components API
```ruby
# GET /api/v1/components/for_system?system_code=X45
# Returns components for a specific system
{
  "system": { ... },
  "components": [
    {
      "component_type": "chain",
      "name": "X45 Chain",
      "specifications": {
        "Chain Width": "50-150 mm",
        "Max Load": "Light duty"
      },
      "compatibility": ["X45"]
    }
  ],
  "summary": {
    "total_components": 5,
    "component_types": ["chain", "drive_unit", "bearing"],
    "system_code": "X45"
  }
}
```

## Testing

### 1. Model Tests
```ruby
# spec/models/system_spec.rb
require 'rails_helper'

RSpec.describe System, type: :model do
  describe 'associations' do
    it { should have_many(:components) }
    it { should have_many(:product_images) }
  end
  
  describe 'validations' do
    it { should validate_presence_of(:system_code) }
    it { should validate_presence_of(:system_name) }
    it { should validate_uniqueness_of(:system_code) }
  end
  
  describe '#load_score' do
    it 'returns correct score for light duty' do
      system = build(:system, load_capacity: 'Light duty')
      expect(system.load_score).to eq(1)
    end
  end
end
```

### 2. Controller Tests
```ruby
# spec/controllers/systems_controller_spec.rb
require 'rails_helper'

RSpec.describe SystemsController, type: :controller do
  describe 'GET #index' do
    it 'returns all systems' do
      get :index
      expect(response).to have_http_status(:success)
      expect(assigns(:systems)).to be_present
    end
  end
  
  describe 'GET #recommendations' do
    it 'returns compatible systems' do
      system = create(:system, system_code: 'X45')
      get :recommendations, params: { id: system.system_code }
      expect(response).to have_http_status(:success)
    end
  end
end
```

## Performance Considerations

### 1. Database Indexes
- All necessary indexes are already created in Supabase
- Consider adding application-specific indexes if needed

### 2. Caching
```ruby
# app/models/system.rb
class System < ApplicationRecord
  # Add caching for frequently accessed data
  def self.cached_all
    Rails.cache.fetch('systems_all', expires_in: 1.hour) do
      all.to_a
    end
  end
  
  def cached_components
    Rails.cache.fetch("system_#{system_code}_components", expires_in: 30.minutes) do
      components.to_a
    end
  end
end
```

### 3. Pagination
```ruby
# app/controllers/systems_controller.rb
def index
  @systems = System.page(params[:page]).per(params[:per_page] || 20)
  # ... rest of the method
end
```

## Security Considerations

### 1. Row Level Security (RLS)
- RLS policies are maintained in Supabase
- Ensure your Rails app respects these policies

### 2. API Authentication
```ruby
# app/controllers/api/v1/base_controller.rb
class Api::V1::BaseController < ApplicationController
  before_action :authenticate_user!
  skip_before_action :verify_authenticity_token
end
```

## Deployment Notes

### 1. Environment Variables
```bash
# .env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### 2. Database Connection
```ruby
# config/database.yml
production:
  adapter: postgresql
  url: <%= ENV['DATABASE_URL'] %>
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
```

This integration guide provides a complete framework for updating your Rails application to work with the new database structure while maintaining backward compatibility and performance. 