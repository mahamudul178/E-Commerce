from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings

class Command(BaseCommand):
    help = 'Setup Google OAuth social application'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=str,
            help='Google OAuth Client ID',
        )
        parser.add_argument(
            '--client-secret',
            type=str,
            help='Google OAuth Client Secret',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing Google app',
        )
    
    def handle(self, *args, **options):
        # Get or create the site
        site, created = Site.objects.get_or_create(
            pk=settings.SITE_ID,
            defaults={
                'domain': '127.0.0.1:8000',
                'name': 'ShopEase Development'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created site: {site.name} ({site.domain})')
            )
        else:
            self.stdout.write(f'Using existing site: {site.name} ({site.domain})')
        
        # Get Google credentials from arguments or settings
        client_id = options.get('client_id') or getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', '')
        client_secret = options.get('client_secret') or getattr(settings, 'GOOGLE_OAUTH2_CLIENT_SECRET', '')
        
        if not client_id or not client_secret:
            self.stdout.write(
                self.style.WARNING(
                    'No Google OAuth credentials provided. You have three options:\n'
                    '1. Set GOOGLE_OAUTH2_CLIENT_ID and GOOGLE_OAUTH2_CLIENT_SECRET in your .env file\n'
                    '2. Use --client-id and --client-secret arguments\n'
                    '3. Run this command later after setting up credentials\n'
                )
            )
            
            # Create a placeholder app for now
            client_id = 'your-google-client-id-here'
            client_secret = 'your-google-client-secret-here'
            self.stdout.write(
                self.style.WARNING('Creating placeholder Google app. Update credentials later!')
            )
        
        # Create or update Google social app
        try:
            google_app = SocialApp.objects.get(provider='google')
            if options.get('force') or not google_app.client_id:
                google_app.client_id = client_id
                google_app.secret = client_secret
                google_app.name = 'Google OAuth'
                google_app.save()
                action = 'Updated'
            else:
                action = 'Found existing'
        except SocialApp.DoesNotExist:
            google_app = SocialApp.objects.create(
                provider='google',
                name='Google OAuth',
                client_id=client_id,
                secret=client_secret,
            )
            action = 'Created'
        
        # Add site to the app
        google_app.sites.add(site)
        
        self.stdout.write(
            self.style.SUCCESS(f'{action} Google OAuth app: {google_app.name}')
        )
        
        # Show current configuration
        self.stdout.write('\nCurrent configuration:')
        self.stdout.write(f'  Provider: {google_app.provider}')
        self.stdout.write(f'  Client ID: {google_app.client_id}')
        self.stdout.write(f'  Secret: {"*" * len(google_app.secret) if google_app.secret else "Not set"}')
        self.stdout.write(f'  Sites: {", ".join([str(s) for s in google_app.sites.all()])}')
        
        if client_id == 'your-google-client-id-here':
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  IMPORTANT: You need to update the Google credentials!\n'
                    'Either:\n'
                    '1. Add to .env file:\n'
                    '   GOOGLE_OAUTH2_CLIENT_ID=your-real-client-id\n'
                    '   GOOGLE_OAUTH2_CLIENT_SECRET=your-real-client-secret\n'
                    '2. Run: python manage.py setup_google_oauth --client-id YOUR_ID --client-secret YOUR_SECRET --force\n'
                    '3. Update manually in Django admin at /admin/socialaccount/socialapp/\n'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✅ Google OAuth setup complete!\n'
                    'You can now use Google sign-in on your site.\n'
                    'Visit: http://127.0.0.1:8000/accounts/login/'
                )
            )