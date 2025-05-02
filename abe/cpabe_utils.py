from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64
import json
import pickle

class SimpleABE:
    def __init__(self):
        self.key_store = {}
        self.policy_store = {}
        os.makedirs('abe/keys', exist_ok=True)
        
    def setup(self):
        """Initialize the encryption system"""
        return True
        
    def encrypt_file(self, file_path, attributes):
        """Encrypt a file with the given attributes"""
        # Generate a new encryption key
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        
        # Read and encrypt the file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        encrypted_data = cipher_suite.encrypt(file_data)
        
        # Store the key and policy
        file_id = os.path.basename(file_path)
        self.key_store[file_id] = key
        self.policy_store[file_id] = attributes
        
        # Save encrypted file
        encrypted_file_path = f"{file_path}.enc"
        with open(encrypted_file_path, 'wb') as f:
            f.write(encrypted_data)
            
        # Save metadata
        self._save_metadata()
        
        return encrypted_file_path
        
    def decrypt_file(self, encrypted_file_path, user_attributes):
        """Decrypt a file if the user has the required attributes"""
        file_id = os.path.basename(encrypted_file_path).replace('.enc', '')
        
        if file_id not in self.key_store:
            raise Exception("File not found in key store")
            
        # Check if user has required attributes
        required_attributes = set(self.policy_store[file_id])
        user_attributes = set(user_attributes)
        
        if not required_attributes.issubset(user_attributes):
            raise Exception("User does not have required attributes for decryption")
            
        # Decrypt the file
        key = self.key_store[file_id]
        cipher_suite = Fernet(key)
        
        with open(encrypted_file_path, 'rb') as f:
            encrypted_data = f.read()
            
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        
        # Save decrypted file
        decrypted_file_path = os.path.join('decrypted', os.path.basename(encrypted_file_path).replace('.enc', ''))
        with open(decrypted_file_path, 'wb') as f:
            f.write(decrypted_data)
            
        return decrypted_file_path
        
    def _save_metadata(self):
        """Save encryption metadata to disk"""
        metadata = {
            'key_store': {k: base64.b64encode(v).decode() for k, v in self.key_store.items()},
            'policy_store': self.policy_store
        }
        
        with open('abe/keys/metadata.pickle', 'wb') as f:
            pickle.dump(metadata, f)
            
    def _load_metadata(self):
        """Load encryption metadata from disk"""
        try:
            with open('abe/keys/metadata.pickle', 'rb') as f:
                metadata = pickle.load(f)
                self.key_store = {k: base64.b64decode(v) for k, v in metadata['key_store'].items()}
                self.policy_store = metadata['policy_store']
        except FileNotFoundError:
            pass

# Create a global instance
abe = SimpleABE()

def setup():
    """Initialize the ABE system"""
    return abe.setup()

def encrypt_file(file_path, attributes):
    """Encrypt a file with the given attributes"""
    return abe.encrypt_file(file_path, attributes)

def decrypt_file(encrypted_file_path, user_attributes):
    """Decrypt a file if the user has the required attributes"""
    return abe.decrypt_file(encrypted_file_path, user_attributes)
