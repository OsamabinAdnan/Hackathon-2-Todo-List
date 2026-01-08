'use client';

import { useState, useEffect } from 'react';
import { AlertTriangleIcon, CheckIcon, XIcon, Eye, EyeOff } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AnimatedCard, AnimatedPage } from '@/components/ui/animate';
import { userApi } from '@/lib/api';
import { DeleteAccountConfirmationModal } from '@/components/settings/DeleteAccountConfirmationModal';

const toastSuccessClassNames = {
  toast: 'glass-toast-success',
  title: 'glass-toast-title',
  description: 'glass-toast-description',
};

const toastErrorClassNames = {
  toast: 'glass-toast-error',
  title: 'glass-toast-title',
  description: 'glass-toast-description',
};

const getErrorMessage = (error: unknown) => {
  if (error instanceof Error) return error.message;
  return 'Something went wrong';
};

const clearClientAuth = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

const dispatchAuthLogoutEvent = () => {
  window.dispatchEvent(
    new CustomEvent('auth-change', {
      detail: { type: 'LOGOUT' },
    })
  );
};

export default function SettingsPage() {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [profileName, setProfileName] = useState('');
  const [profileEmail, setProfileEmail] = useState('');
  const [isLoadingProfile, setIsLoadingProfile] = useState(false);
  const [isLoadingPassword, setIsLoadingPassword] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  useEffect(() => {
    // Load current user data from localStorage if available
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        setProfileName(user.name || '');
        setProfileEmail(user.email || '');
      } catch (e) {
        console.error('Failed to parse stored user:', e);
      }
    }
  }, []);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();

    if (newPassword !== confirmNewPassword) {
      toast.error('New passwords do not match', {
        className: toastErrorClassNames.toast,
        classNames: {
          title: toastErrorClassNames.title,
          description: toastErrorClassNames.description,
        },
      });
      return;
    }

    if (newPassword.length < 6) {
      toast.error('New password must be at least 6 characters long', {
        className: toastErrorClassNames.toast,
        classNames: {
          title: toastErrorClassNames.title,
          description: toastErrorClassNames.description,
        },
      });
      return;
    }

    setIsLoadingPassword(true);
    try {
      await userApi.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      toast.success('Password changed successfully!', {
        className: toastSuccessClassNames.toast,
        classNames: {
          title: toastSuccessClassNames.title,
          description: toastSuccessClassNames.description,
        },
      });
      setCurrentPassword('');
      setNewPassword('');
      setConfirmNewPassword('');
    } catch (error: any) {
      toast.error(error.message || 'Failed to change password', {
        className: toastErrorClassNames.toast,
        classNames: {
          title: toastErrorClassNames.title,
          description: toastErrorClassNames.description,
        },
      });
    } finally {
      setIsLoadingPassword(false);
    }
  };

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();

    setIsLoadingProfile(true);
    try {
      const updatedUser = await userApi.updateProfile({
        name: profileName,
        email: profileEmail,
      });

      // Update local storage
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        const user = JSON.parse(storedUser);
        localStorage.setItem('user', JSON.stringify({ ...user, ...updatedUser }));
      }

      toast.success('Profile updated successfully!', {
        className: toastSuccessClassNames.toast,
        classNames: {
          title: toastSuccessClassNames.title,
          description: toastSuccessClassNames.description,
        },
      });
    } catch (error: any) {
      toast.error(error.message || 'Failed to update profile', {
        className: toastErrorClassNames.toast,
        classNames: {
          title: toastErrorClassNames.title,
          description: toastErrorClassNames.description,
        },
      });
    } finally {
      setIsLoadingProfile(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  const handleDeleteAccount = async () => {
    try {
      await userApi.deleteAccount();
      setIsDeleteModalOpen(false);

      // Show success toast with glassmorphism style
      toast.success(
        'Your account has been deleted successfully and you are being redirected.',
        {
          className: toastSuccessClassNames.toast,
          classNames: {
            title: toastSuccessClassNames.title,
            description: toastSuccessClassNames.description,
          },
          duration: 3000,
        }
      );

      // Delay redirection slightly to show toast
      setTimeout(() => {
        dispatchAuthLogoutEvent();
        clearClientAuth();
        window.location.href = '/login';
      }, 1500);

    } catch (error) {
      setIsDeleteModalOpen(false);
      toast.error(getErrorMessage(error), {
        className: toastErrorClassNames.toast,
        classNames: {
          title: toastErrorClassNames.title,
          description: toastErrorClassNames.description,
        },
      });
    }
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-indigo-950 dark:to-purple-950 flex flex-col">
      <DeleteAccountConfirmationModal
        isOpen={isDeleteModalOpen}
        onConfirm={handleDeleteAccount}
        onCancel={() => setIsDeleteModalOpen(false)}
      />
      <AnimatedPage className="flex-1">
        <div className="space-y-6 max-w-7xl mx-auto px-2 xs:px-4 sm:px-6 lg:px-8 py-4 xs:py-6 sm:py-8">
          <AnimatedCard delay={0.1}>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
          </AnimatedCard>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Profile Settings Card */}
            <AnimatedCard delay={0.2}>
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="text-gray-900 dark:text-white">Profile Settings</CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleProfileUpdate} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Full Name
                      </label>
                      <Input
                        type="text"
                        value={profileName}
                        onChange={(e) => setProfileName(e.target.value)}
                        placeholder="John Doe"
                        className="bg-white/30 backdrop-blur-sm border border-white/30 dark:border-gray-600/50 text-gray-900 dark:text-white rounded-lg py-2 px-3 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Email Address
                      </label>
                      <Input
                        type="email"
                        value={profileEmail}
                        onChange={(e) => setProfileEmail(e.target.value)}
                        placeholder="john@example.com"
                        className="bg-white/30 backdrop-blur-sm border border-white/30 dark:border-gray-600/50 text-gray-900 dark:text-white rounded-lg py-2 px-3 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                      />
                    </div>

                    <Button
                      type="submit"
                      disabled={isLoadingProfile}
                      className="w-full bg-indigo-600/80 backdrop-blur-sm hover:bg-indigo-700/80 text-white py-2 px-4 rounded-lg transition-all duration-200 disabled:opacity-50"
                    >
                      {isLoadingProfile ? 'Updating...' : 'Update Profile'}
                    </Button>
                  </form>
                </CardContent>
            </Card>
          </AnimatedCard>

          {/* Password Change Card */}
          <AnimatedCard delay={0.3}>
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Change Password</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handlePasswordChange} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Current Password
                    </label>
                    <div className="relative">
                      <Input
                        type={showCurrentPassword ? 'text' : 'password'}
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        placeholder="Enter current password"
                        required
                        className="bg-white/30 backdrop-blur-sm border border-white/30 dark:border-gray-600/50 text-gray-900 dark:text-white rounded-lg py-2 px-3 pr-10 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                      />
                      <button
                        type="button"
                        onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                        aria-label={showCurrentPassword ? 'Hide password' : 'Show password'}
                      >
                        {showCurrentPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      New Password
                    </label>
                    <div className="relative">
                      <Input
                        type={showNewPassword ? 'text' : 'password'}
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="Enter new password"
                        required
                        className="bg-white/30 backdrop-blur-sm border border-white/30 dark:border-gray-600/50 text-gray-900 dark:text-white rounded-lg py-2 px-3 pr-10 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                      />
                      <button
                        type="button"
                        onClick={() => setShowNewPassword(!showNewPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                        aria-label={showNewPassword ? 'Hide password' : 'Show password'}
                      >
                        {showNewPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Confirm New Password
                    </label>
                    <div className="relative">
                      <Input
                        type={showConfirmPassword ? 'text' : 'password'}
                        value={confirmNewPassword}
                        onChange={(e) => setConfirmNewPassword(e.target.value)}
                        placeholder="Confirm new password"
                        required
                        className="bg-white/30 backdrop-blur-sm border border-white/30 dark:border-gray-600/50 text-gray-900 dark:text-white rounded-lg py-2 px-3 pr-10 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                        aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                      >
                        {showConfirmPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  <Button
                    type="submit"
                    disabled={isLoadingPassword}
                    className="w-full bg-indigo-600/80 backdrop-blur-sm hover:bg-indigo-700/80 text-white py-2 px-4 rounded-lg transition-all duration-200 disabled:opacity-50"
                  >
                    {isLoadingPassword ? 'Changing...' : 'Change Password'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </AnimatedCard>
          </div>

        {/* Account Management Card */}
        <AnimatedCard delay={0.4}>
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-gray-900 dark:text-white">Account Management</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-4 bg-red-500/10 dark:bg-red-900/20 rounded-lg">
                  <div>
                    <h3 className="font-medium text-red-700 dark:text-red-300">Delete Account</h3>
                    <p className="text-sm text-red-600 dark:text-red-400">Permanently remove your account and all data</p>
                  </div>
                  <Button
                    variant="destructive"
                    onClick={() => setIsDeleteModalOpen(true)}
                    className="bg-red-500/80 backdrop-blur-sm hover:bg-red-600/80 text-white"
                  >
                    Delete Account
                  </Button>
                </div>

                <div className="flex justify-between items-center p-4 bg-yellow-500/10 dark:bg-yellow-900/20 rounded-lg">
                  <div>
                    <h3 className="font-medium text-yellow-700 dark:text-yellow-300">Log Out</h3>
                    <p className="text-sm text-yellow-600 dark:text-yellow-400">End your current session</p>
                  </div>
                  <Button
                    variant="outline"
                    onClick={handleLogout}
                    className="border-yellow-500/50 text-yellow-700 dark:text-yellow-300 hover:bg-yellow-500/20 dark:hover:bg-yellow-900/30"
                  >
                    Log Out
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </AnimatedCard>
      </div>
      </AnimatedPage>
    </div>
  );
}