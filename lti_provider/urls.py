
from django.urls import include, path
from lti_provider.views import LTIConfigView, LTILandingPage, LTIRoutingView, \
    LTICourseEnableView, LTIPostGrade, LTIFailAuthorization, LTICourseConfigure

urlpatterns = [
    path('config.xml', LTIConfigView.as_view(), name='lti-config'),
    path('auth', LTIFailAuthorization.as_view(), name='lti-fail-auth'),
    path('course/config', LTICourseConfigure.as_view(), name='lti-course-config'),
    path('course/enable/', LTICourseEnableView.as_view(), name='lti-course-enable'),
    path('landing/', LTILandingPage.as_view(), name='lti-landing-page'),
    path('grade/', LTIPostGrade.as_view(), name='lti-post-grade'),
    path('', LTIRoutingView.as_view(), name='lti-login'),
    path('assignment/<slug:assignment_name>/', LTIRoutingView.as_view(), name='lti-assignment-view'),
]
