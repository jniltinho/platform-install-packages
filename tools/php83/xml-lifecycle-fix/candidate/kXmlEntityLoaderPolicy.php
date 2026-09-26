<?php

/**
 * Request-local XML policy scopes for synchronous SOAP calls on PHP 8.3.
 * Not an isolation mechanism for fibers or unrelated parsers inside a SOAP call.
 */
final class kXmlEntityLoaderPolicy
{
    private static $installed = false;
    private static $deny;
    private static $previous;
    private static $scopes = array();

    private static function denyLoader()
    {
        if (self::$deny === null) {
            self::$deny = static function ($public, $system, $context) {
                return null;
            };
        }
        return self::$deny;
    }

    private static function requireRuntime()
    {
        if (!function_exists('libxml_get_external_entity_loader')) {
            throw new RuntimeException('XML policy requires the native loader getter');
        }
    }

    public static function installDefaultDeny()
    {
        self::requireRuntime();
        if (self::$scopes) {
            throw new LogicException('Cannot initialize XML policy inside a SOAP scope');
        }
        $current = libxml_get_external_entity_loader();
        $deny = self::denyLoader();
        if (self::$installed) {
            if ($current !== $deny) {
                throw new LogicException('XML policy initialization would replace a foreign loader');
            }
            return;
        }
        self::$previous = $current;
        if (!libxml_set_external_entity_loader($deny)) {
            throw new RuntimeException('Cannot install XML deny policy');
        }
        self::$installed = true;
    }

    public static function beginSoapScope()
    {
        self::requireRuntime();
        $previous = libxml_get_external_entity_loader();
        $active = self::$installed && $previous === self::denyLoader()
            ? self::$previous : $previous;
        // The caller receives only identity; mutable state stays private.
        $token = new stdClass();
        self::$scopes[] = array(
            'token' => $token, 'previous' => $previous, 'active' => $active,
            'wrappers' => array(),
        );
        $index = count(self::$scopes) - 1;
        try {
            foreach (array('http', 'https') as $scheme) {
                if (!in_array($scheme, stream_get_wrappers(), true)) {
                    if (!stream_wrapper_restore($scheme)) {
                        throw new RuntimeException('Cannot restore SOAP wrapper ' . $scheme);
                    }
                    self::$scopes[$index]['wrappers'][] = $scheme;
                }
            }
            if ($active !== $previous && !libxml_set_external_entity_loader($active)) {
                throw new RuntimeException('Cannot delegate SOAP XML loader');
            }
            if (libxml_get_external_entity_loader() !== $active) {
                throw new RuntimeException('SOAP XML loader identity was not installed');
            }
        } catch (Throwable $error) {
            // Setup may have restored only one wrapper; never leak that partial state.
            self::endSoapScope($token, $error);
            throw $error;
        }
        return $token;
    }

    public static function endSoapScope($token, $primary = null)
    {
        $last = count(self::$scopes) - 1;
        if ($last < 0 || self::$scopes[$last]['token'] !== $token) {
            self::failClosed(new LogicException('XML scopes must close in LIFO order'), $primary);
        }
        $scope = self::$scopes[$last];
        try {
            if (libxml_get_external_entity_loader() !== $scope['active']) {
                throw new LogicException('Foreign XML loader mutation inside a SOAP scope');
            }
            if (!libxml_set_external_entity_loader($scope['previous'])) {
                throw new RuntimeException('Cannot restore previous XML loader');
            }
            if (libxml_get_external_entity_loader() !== $scope['previous']) {
                throw new RuntimeException('Previous XML loader identity was not restored');
            }
            foreach (array_reverse($scope['wrappers']) as $scheme) {
                if (in_array($scheme, stream_get_wrappers(), true) &&
                    !stream_wrapper_unregister($scheme)) {
                    throw new RuntimeException('Cannot remove owned SOAP wrapper ' . $scheme);
                }
            }
            array_pop(self::$scopes);
        } catch (Throwable $cleanup) {
            self::failClosed($cleanup, $primary);
        }
    }

    private static function failClosed($cause, $primary)
    {
        $failures = array(get_class($cause) . ': ' . $cause->getMessage());
        try {
            if (!libxml_set_external_entity_loader(self::denyLoader())) {
                throw new RuntimeException('Deny fallback returned false');
            }
        } catch (Throwable $error) {
            $failures[] = 'Deny fallback failed: ' . $error->getMessage();
        }
        foreach (array_reverse(self::$scopes) as $scope) {
            foreach (array_reverse($scope['wrappers']) as $scheme) {
                try {
                    if (in_array($scheme, stream_get_wrappers(), true) &&
                        !stream_wrapper_unregister($scheme)) {
                        throw new RuntimeException('Wrapper cleanup returned false for ' . $scheme);
                    }
                } catch (Throwable $error) {
                    $failures[] = 'Wrapper cleanup failed: ' . $error->getMessage();
                }
            }
        }
        self::$scopes = array();
        // Keep the original SoapFault as the causal exception when cleanup also fails.
        throw new RuntimeException(
            'XML scope cleanup failed; ' . implode('; ', $failures),
            0,
            $primary instanceof Throwable ? $primary : $cause
        );
    }
}
