using UnityEngine;
using static Weapon;

public class SoundManager : MonoBehaviour
{
    public static SoundManager Instance { get; set; }

    public AudioSource shootingChannel;

    public AudioClip P1911Shot;
    public AudioClip M4Shot;

    public AudioSource reloadingSound1911;
    public AudioSource reloadingSoundM4;

    public AudioSource emptyMagazineSound1911;
    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
        }
        else
        {
            Instance = this;
        }
    }

    public void playShootingSound(WeaponModel weapon)
    {
        switch (weapon)
        {
            case WeaponModel.pistol1911:
                shootingChannel.PlayOneShot(P1911Shot);
                break;
            case WeaponModel.M4:
                shootingChannel.PlayOneShot(M4Shot);
                break;
        }
    }

    public void playReloadSound(WeaponModel weapon)
    {
        switch (weapon)
        {
            case WeaponModel.pistol1911:
                reloadingSound1911.Play();
                break;
            case WeaponModel.M4:
                reloadingSoundM4.Play();
                break;
        }
    }
}
