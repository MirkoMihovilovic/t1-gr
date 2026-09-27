#version 330 core

in vec3 fragPos;
in vec3 fragNormal;

out vec4 outColor;

vec3 computeDirectionalLight(vec3 normal) {

    vec3 direction = vec3(1, 1, 0);

    vec3 ambient = vec3(0.3, 0.3, 0.3);
    vec3 diffuse = vec3(0.3, 0.3, 0.3);

    vec3 color = vec3(118 / 255.0, 209 / 255.0, 79.0 / 255.0);

    vec3 ambientT = ambient * color;

    float diff = max(dot(normal, direction), 0.0);
    vec3 diffuseT = diffuse * (diff * color);

    return (ambientT + diffuseT);
}

void main()
{

    vec3 normal = normalize(fragNormal);

    vec3 finalColor = computeDirectionalLight(normal);

    float snowHeight = 1.0;
    float blendZone = 0.2;
    float snowFactor = clamp((fragPos.y - snowHeight) / blendZone, 0.0, 1.0);

    finalColor = mix(finalColor, vec3(1.0), snowFactor);

    outColor = vec4(finalColor, 1.0);
}
