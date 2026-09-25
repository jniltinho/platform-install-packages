<?php
// Diagnostic: distinguish ArrayObject storage/property behavior from Registry.
require_once 'Zend/Registry.php';
foreach (array('ArrayObject', 'Zend_Registry') as $class) {
    foreach (array(0, 1, 2, 3) as $flags) {
        foreach (array(false, true) as $prime) {
          foreach (array('literal', 'variable') as $assignment) {
            $object = new $class(array('initial' => null), $flags);
            $primed = null;
            if ($prime) {
                try { $primed = $object->offsetExists('initial'); }
                catch (Throwable $error) { $primed = get_class($error); }
            }
            if ($assignment === 'literal') { $object->dynamicProbe = 'dynamic'; }
            else { $key = 'dynamicProbe'; $object->$key = 'dynamic'; }
            $out[] = array('class' => $class, 'assignment' => $assignment, 'flags' => $flags, 'prime' => $prime,
                'primed' => $primed, 'array_copy' => $object->getArrayCopy(),
                'public_properties' => get_object_vars($object), 'cast' => (array) $object);
            if ($assignment === 'literal') { $object->initial = 'replaced'; }
            else { $key = 'initial'; $object->$key = 'replaced'; }
            $out[] = array('existing_key_write' => true, 'class' => $class,
                'assignment' => $assignment, 'flags' => $flags, 'prime' => $prime, 'array_copy' => $object->getArrayCopy(),
                'public_properties' => get_object_vars($object), 'cast' => (array) $object);
          }
        }
    }
}
