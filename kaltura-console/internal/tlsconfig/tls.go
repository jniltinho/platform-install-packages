// Package tlsconfig manages persistent standalone TLS without replacing operator certificates.
package tlsconfig

import (
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/pem"
	"errors"
	"fmt"
	"math/big"
	"net"
	"os"
	"path/filepath"
	"time"
)

// Prepare loads an explicit pair, or creates/reuses a private self-signed pair in dir.
// A partial pair is an error: certificate identity never changes silently.
func Prepare(certFile, keyFile, dir, host string) (*tls.Config, error) {
	if (certFile == "") != (keyFile == "") {
		return nil, errors.New("TLS requires both certificate and key")
	}
	if certFile == "" {
		if dir == "" {
			return nil, errors.New("server.tls_dir is required for self-signed TLS")
		}
		if err := os.MkdirAll(dir, 0o700); err != nil {
			return nil, err
		}
		info, err := os.Lstat(dir)
		if err != nil {
			return nil, err
		}
		if !info.IsDir() || info.Mode().Perm()&0o022 != 0 {
			return nil, errors.New("TLS directory must be a real directory not writable by group/others")
		}
		certFile, keyFile = filepath.Join(dir, "cert.pem"), filepath.Join(dir, "key.pem")
		certInfo, ce := os.Lstat(certFile)
		keyInfo, ke := os.Lstat(keyFile)
		switch {
		case errors.Is(ce, os.ErrNotExist) && errors.Is(ke, os.ErrNotExist):
			if err := generate(certFile, keyFile, host); err != nil {
				return nil, err
			}
		case ce != nil || ke != nil:
			return nil, fmt.Errorf("incomplete or unreadable TLS pair in %s: %w", dir, errors.Join(ce, ke))
		default:
			if !certInfo.Mode().IsRegular() || !keyInfo.Mode().IsRegular() || keyInfo.Mode().Perm() != 0o600 {
				return nil, errors.New("stored TLS pair must be regular files with private key mode 0600")
			}
		}
	}
	pair, err := tls.LoadX509KeyPair(certFile, keyFile)
	if err != nil {
		return nil, fmt.Errorf("loading TLS pair: %w", err)
	}
	cert, err := x509.ParseCertificate(pair.Certificate[0])
	if err != nil {
		return nil, err
	}
	now := time.Now()
	if now.Before(cert.NotBefore) || now.After(cert.NotAfter) {
		return nil, errors.New("TLS certificate is not currently valid; replace it explicitly")
	}
	return &tls.Config{MinVersion: tls.VersionTLS12, Certificates: []tls.Certificate{pair}}, nil
}

func generate(certFile, keyFile, host string) error {
	key, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		return err
	}
	serial, err := rand.Int(rand.Reader, new(big.Int).Lsh(big.NewInt(1), 128))
	if err != nil {
		return err
	}
	now := time.Now()
	cert := &x509.Certificate{SerialNumber: serial, Subject: pkix.Name{CommonName: "Kaltura Console (self-signed)"},
		NotBefore: now.Add(-5 * time.Minute), NotAfter: now.AddDate(10, 0, 0),
		KeyUsage: x509.KeyUsageDigitalSignature, ExtKeyUsage: []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth},
		BasicConstraintsValid: true, DNSNames: []string{"localhost"},
		IPAddresses: []net.IP{net.ParseIP("127.0.0.1"), net.ParseIP("::1")}}
	if ip := net.ParseIP(host); ip != nil {
		if !ip.IsUnspecified() {
			cert.IPAddresses = append(cert.IPAddresses, ip)
		}
	} else if host != "" && host != "localhost" {
		cert.DNSNames = append(cert.DNSNames, host)
	}
	if hostname, err := os.Hostname(); err == nil && hostname != "" {
		cert.DNSNames = append(cert.DNSNames, hostname)
	}
	addrs, err := net.InterfaceAddrs()
	if err != nil {
		return err
	}
	for _, addr := range addrs {
		if ip, _, err := net.ParseCIDR(addr.String()); err == nil {
			cert.IPAddresses = append(cert.IPAddresses, ip)
		}
	}
	der, err := x509.CreateCertificate(rand.Reader, cert, cert, &key.PublicKey, key)
	if err != nil {
		return err
	}
	keyDER, err := x509.MarshalPKCS8PrivateKey(key)
	if err != nil {
		return err
	}
	// O_EXCL rejects concurrent generation and symlinks; leave partial material for explicit recovery.
	if err := writeNew(keyFile, pem.EncodeToMemory(&pem.Block{Type: "PRIVATE KEY", Bytes: keyDER}), 0o600); err != nil {
		return err
	}
	return writeNew(certFile, pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: der}), 0o644)
}
func writeNew(path string, data []byte, mode os.FileMode) error {
	f, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, mode)
	if err != nil {
		return err
	}
	_, err = f.Write(data)
	return errors.Join(err, f.Close())
}
