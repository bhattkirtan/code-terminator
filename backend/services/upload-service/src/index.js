const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const multer = require('multer');
const { Storage } = require('@google-cloud/storage');
const { Firestore } = require('@google-cloud/firestore');
const sharp = require('sharp');
const { v4: uuidv4 } = require('uuid');
const Joi = require('joi');

const app = express();
const port = process.env.PORT || 8080;

// Initialize Google Cloud services
const storage = new Storage();
const firestore = new Firestore();
const bucket = storage.bucket(process.env.STORAGE_BUCKET || 'snapit');

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true
}));
app.use(express.json());

// Multer configuration for file uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif|css|scss|pdf|doc|docx/;
    const extname = allowedTypes.test(file.originalname.toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);
    
    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only images, CSS, and documents are allowed.'));
    }
  }
});

// Validation schemas
const uploadSchema = Joi.object({
  projectId: Joi.string().required(),
  metadata: Joi.object().optional()
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'upload-service',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// Upload endpoint
app.post('/api/upload', upload.array('files', 10), async (req, res) => {
  try {
    // Validate request body
    const { error, value } = uploadSchema.validate(req.body);
    if (error) {
      return res.status(400).json({
        status: 'error',
        message: error.details[0].message
      });
    }

    const { projectId, metadata = {} } = value;
    const files = req.files;

    if (!files || files.length === 0) {
      return res.status(400).json({
        status: 'error',
        message: 'No files provided'
      });
    }

    const uploadedFiles = [];
    const storageUrls = [];

    // Process each file
    for (const file of files) {
      const fileId = uuidv4();
      const fileExtension = file.originalname.split('.').pop();
      const fileName = `${fileId}.${fileExtension}`;
      
      // Determine storage path based on file type
      let storagePath;
      if (file.mimetype.startsWith('image/')) {
        storagePath = `${projectId}/context/ui-images/${fileName}`;
      } else if (file.mimetype.includes('css')) {
        storagePath = `${projectId}/context/assets/css/${fileName}`;
      } else {
        storagePath = `${projectId}/context/assets/docs/${fileName}`;
      }

      // Optimize images using Sharp
      let processedBuffer = file.buffer;
      if (file.mimetype.startsWith('image/')) {
        processedBuffer = await sharp(file.buffer)
          .resize(1920, 1080, { fit: 'inside', withoutEnlargement: true })
          .jpeg({ quality: 85 })
          .toBuffer();
      }

      // Upload to Cloud Storage
      const cloudFile = bucket.file(storagePath);
      await cloudFile.save(processedBuffer, {
        metadata: {
          contentType: file.mimetype,
          cacheControl: 'public, max-age=31536000',
        },
      });

      // Make file publicly readable
      await cloudFile.makePublic();

      const publicUrl = `https://storage.googleapis.com/${bucket.name}/${storagePath}`;

      // Store metadata in Firestore
      const assetDoc = {
        id: fileId,
        projectId,
        type: file.mimetype.startsWith('image/') ? 'image' : 
              file.mimetype.includes('css') ? 'css' : 'document',
        originalName: file.originalname,
        fileName,
        url: publicUrl,
        size: processedBuffer.length,
        mimetype: file.mimetype,
        metadata,
        createdAt: new Date(),
        updatedAt: new Date()
      };

      await firestore
        .collection('projects')
        .doc(projectId)
        .collection('assets')
        .doc(fileId)
        .set(assetDoc);

      uploadedFiles.push(assetDoc);
      storageUrls.push(publicUrl);
    }

    res.json({
      status: 'success',
      uploadedFiles,
      storageUrls,
      count: uploadedFiles.length
    });

  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({
      status: 'error',
      message: 'Internal server error',
      details: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({
        status: 'error',
        message: 'File too large. Maximum size is 10MB.'
      });
    }
  }
  
  console.error('Unhandled error:', error);
  res.status(500).json({
    status: 'error',
    message: 'Internal server error'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    status: 'error',
    message: 'Endpoint not found'
  });
});

app.listen(port, () => {
  console.log(`📤 Upload Service running on port ${port}`);
});

module.exports = app;
