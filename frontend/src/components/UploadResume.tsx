// components/UploadResume.tsx
import React, { useState, ChangeEvent } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/contexts/AuthContext';

interface UploadResumeProps {
  onUploadSuccess?: () => void;
}

const UploadResume: React.FC<UploadResumeProps> = ({ onUploadSuccess }) => {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const { user } = useAuth();

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    setResumeFile(file || null);
    setUploadStatus('');
  };

  const handleUpload = async () => {
    if (!resumeFile) {
      setUploadStatus('Please select a file to upload.');
      return;
    }

    if (!user?.email) {
      setUploadStatus('❌ User not logged in.');
      return;
    }

    const formData = new FormData();
    formData.append('resume', resumeFile);
    formData.append('consultant_email', user.email);

    try {
      const response = await fetch('http://localhost:8000/upload-resume', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadStatus('✅ Resume uploaded and analyzed successfully!');
        console.log('Analysis result:', result);
        
        // Call the success callback to refresh parent data
        if (onUploadSuccess) {
          onUploadSuccess();
        }
      } else {
        const errorText = await response.text();
        setUploadStatus(`❌ Failed to upload resume: ${errorText}`);
      }
    } catch (error) {
      console.error(error);
      setUploadStatus('⚠️ An error occurred while uploading.');
    }
  };

  return (
    <Card className="mt-6">
      <CardHeader>
        <CardTitle>Upload Resume</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="resume">Select Resume File (PDF/DOCX/TXT)</Label>
          <Input
            id="resume"
            type="file"
            accept=".pdf,.doc,.docx,.txt"
            onChange={handleFileChange}
          />
        </div>
        <Button onClick={handleUpload}>Upload</Button>
        {uploadStatus && <p className="text-sm text-blue-600">{uploadStatus}</p>}
      </CardContent>
    </Card>
  );
};

export default UploadResume;
